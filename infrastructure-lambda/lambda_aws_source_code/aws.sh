log_message() {
    local message="$1"
    local session="${SESSION_ID:-unknown}"
    echo "[${session}]-${message}" >&2
}

get_chunk() {
    # Function to retrieve a specific chunk from S3
    CHUNK_NAME=$1
    log_message "Retrieving chunk: $CHUNK_NAME"
    log_message "command: aws s3 cp s3://$CHUNKS_BUCKET/$CHUNK_NAME /tmp/$CHUNK_NAME"

    if aws s3 cp "s3://$CHUNKS_BUCKET/$CHUNK_NAME" "/tmp/$CHUNK_NAME" >&2; then
        log_message "Download the chunk from S3"
        # aws s3 cp "s3://${CHUNKS_BUCKET}/${CHUNK_NAME}" "/tmp/${CHUNK_NAME}" >&2
        log_message "Chunk $CHUNK_NAME downloaded to /tmp/${CHUNK_NAME}"
        cat /tmp/${CHUNK_NAME}
        # Clean up the downloaded chunk
        rm -f "/tmp/${CHUNK_NAME}"
        Remove the chunk from S3 after successful download and processing
        log_message "Removing chunk $CHUNK_NAME from S3"
        if aws s3 rm "s3://$CHUNKS_BUCKET/$CHUNK_NAME" >&2; then
            log_message "Successfully removed chunk $CHUNK_NAME from S3"
        else
            log_message "Failed to remove chunk $CHUNK_NAME from S3, but processing continues"
        fi
    else
        log_message "Impossible to download the chunk from S3"
        echo "ERROR: Impossible to download the chunk $CHUNK_NAME. Please try another method."
    fi

}

function handler() {

    TIMESTAMP=$(date +%s%3N)

    # Detect event format (MCP vs Bedrock Agent)
    if echo "$EVENT_DATA" | jq -e '.bash_command' > /dev/null 2>&1; then
        # MCP format from AgentCore Gateway (flat structure)
        log_message "Detected MCP event format"
        
        AWS_ACCESS_KEY_ID_to_use=$(echo $EVENT_DATA | jq -r '.AWS_ACCESS_KEY_ID // ""')
        AWS_SESSION_TOKEN_to_use=$(echo $EVENT_DATA | jq -r '.AWS_SESSION_TOKEN // ""')
        AWS_SECRET_ACCESS_KEY_to_use=$(echo $EVENT_DATA | jq -r '.AWS_SECRET_ACCESS_KEY // ""')
        AWS_REGION_to_use=$(echo $EVENT_DATA | jq -r '.REGION // ""')
        BASHCOMMAND=$(echo $EVENT_DATA | jq -r '.bash_command // ""')
        SESSION_ID="mcp-session"
        IS_MCP=true
    else
        # Bedrock Agent format
        log_message "Detected Bedrock Agent event format"
        
        AWS_ACCESS_KEY_ID_to_use=$(echo $EVENT_DATA | jq -r '.parameters[] | select(.name=="AWS_ACCESS_KEY_ID") | .value')
        AWS_SESSION_TOKEN_to_use=$(echo $EVENT_DATA | jq -r '.parameters[] | select(.name=="AWS_SESSION_TOKEN") | .value')
        AWS_SECRET_ACCESS_KEY_to_use=$(echo $EVENT_DATA | jq -r '.parameters[] | select(.name=="AWS_SECRET_ACCESS_KEY") | .value')
        AWS_REGION_to_use=$(echo $EVENT_DATA | jq -r '.parameters[] | select(.name=="REGION") | .value')
        SESSION_ID=$(echo $EVENT_DATA | jq -r '.sessionId')
        BASHCOMMAND=$(echo $EVENT_DATA | jq -r '.parameters[] | select(.name=="bash_command") | .value')
        IS_MCP=false
    fi

    log_message "EVENT_DATA=$EVENT_DATA"

    if [ -z "$AWS_SESSION_TOKEN_to_use" ]; then
        #no token provided
        COMMAND_TO_EXECUTE="AWS_REGION=$AWS_REGION_to_use AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID_to_use AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY_to_use ; unset AWS_SESSION_TOKEN; $BASHCOMMAND 2>&1"
    else
        COMMAND_TO_EXECUTE="AWS_REGION=$AWS_REGION_to_use AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID_to_use AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY_to_use AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN_to_use; $BASHCOMMAND 2>&1"
    fi

    log_message "COMMAND_TO_EXECUTE=$BASHCOMMAND"
    # Check if BASHCOMMAND contains "get_chunk": in this case no need to change the AWS creds
    if [[ "$BASHCOMMAND" == *"get_chunk"* ]]; then
        log_message "get_chunk command detected"
        COMMAND_TO_EXECUTE="$BASHCOMMAND"
    fi

    set +e
    set +u
    set +o pipefail

    # Escape quotes and backslashes in the command for proper JSON formatting
    ESCAPED_COMMAND=$(echo "$BASHCOMMAND" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')

    send_log_result=$(AWS_REGION=us-west-2 aws logs put-log-events --log-group-name "/aws/lambda/strands-agents-debug-dev" --log-stream-name "cli-commands" \
        --log-events "[{\"timestamp\": $(date +%s000), \"message\": \"$ESCAPED_COMMAND\"}]")
    # log_message "send_log_result = $send_log_result" >&2

    RESULT=$(eval $COMMAND_TO_EXECUTE)

    EXIT_CODE=$?
    # Measure the size of RESULT in bytes
    RESULT_SIZE=${#RESULT}
    log_message "RESULT_SIZE=${RESULT_SIZE} bytes"

    # if [ $RESULT_SIZE -gt 24576 ]; then
    #     log_message "WARNING: Result size exceeds 24KB, which may cause issues"
    #     # Truncate if needed
    #     RESULT="the output is too long, retry with a more selective command. Here the first part of the output: ${RESULT:0:24576}"
    # fi

    # Handle large results by splitting into chunks
    if [ $RESULT_SIZE -gt 24576 ]; then
        log_message "WARNING: Result size exceeds 24KB, splitting into chunks"
        TOO_LONG_RESULT=$RESULT

        RESULT="the output is too long, so you can get the result in chunks using the command 'get_chunk' followed by the chunk name. The chunk names you can retrieve are: "

        # Create a SHA-256 hash of the BASHCOMMAND to uniquely identify this execution
        COMMAND_HASH=$(echo -n "$BASHCOMMAND" | sha256sum | cut -d' ' -f1)
        log_message "Command hash: $COMMAND_HASH"

        # Use the hash in our S3 path for better organization and tracking

        # Create a temporary directory for chunks
        TIMESTAMP=$(date +%s)
        CHUNK_DIR="/tmp/result_chunks_${SESSION_ID}_${TIMESTAMP}"
        mkdir -p "$CHUNK_DIR"

        # Split the result into chunks of approximately 24KB
        CHUNK_SIZE=24000
        TOTAL_CHUNKS=$(((RESULT_SIZE + CHUNK_SIZE - 1) / CHUNK_SIZE))
        log_message "Total chunks: $TOTAL_CHUNKS"
        for ((i = 0; i < TOTAL_CHUNKS; i++)); do
            START_POS=$((i * CHUNK_SIZE))
            CHUNK="${TOO_LONG_RESULT:$START_POS:$CHUNK_SIZE}"
            CHUNK_FILE_NAME="${SESSION_ID}-${TIMESTAMP}-${i}.txt"
            CHUNK_FILE_PATH="${CHUNK_DIR}/${CHUNK_FILE_NAME}"

            echo "$CHUNK" >"$CHUNK_FILE_PATH"
            log_message "Chunk $i saved to ${CHUNK_FILE_PATH}"

            # Upload chunk to S3 bucket
            # S3_PATH="results/${SESSION_ID}/${TIMESTAMP}/chunk_${i}.txt"
            if aws s3 cp "$CHUNK_FILE_PATH" "s3://${CHUNKS_BUCKET}/${CHUNK_FILE_NAME}" >&2; then
                log_message "Chunk $i uploaded to s3://${CHUNKS_BUCKET}/${CHUNK_FILE_NAME}"

                RESULT="$RESULT $CHUNK_FILE_NAME,"
            else
                log_message "Failed to upload chunk $i to S3 bucket"
                RESULT="the output is too long, retry with a more selective command. Here the first part of the output: ${RESULT:0:24576}"
                # Exit the loop and skip other chunks since we already encountered an error
                break
            fi
            rm -f "$CHUNK_FILE_PATH"
        done

    fi

    set -euo pipefail

    log_message "RESULT=$RESULT"

    # Check event format for response
    if [ "$IS_MCP" = true ]; then
        # MCP response format
        if [ $EXIT_CODE -eq 0 ]; then
            updated_json=$(jq -n \
                --arg result "$RESULT" \
                '{
                    content: [{type: "text", text: $result}],
                    isError: false
                }')
        else
            updated_json=$(jq -n \
                --arg result "$RESULT" \
                '{
                    content: [{type: "text", text: $result}],
                    isError: true
                }')
        fi
    else
        # Bedrock Agent response format
        input_actionGroup=$(echo $EVENT_DATA | jq -r '.actionGroup')
        input_function=$(echo $EVENT_DATA | jq -r '.function')

        template_answer=$(
            cat <<EOF
{
    "messageVersion": "1.0",
    "response": {
        "actionGroup": "string",
        "function": "string",
        "functionResponse": {
            "responseBody": {
                "TEXT": {
                    "body": "JSON-formatted string"
                }
            }
        }
    }
}
EOF
        )

        # Check if command executed successfully
        if [ $EXIT_CODE -eq 0 ]; then
            updated_json=$(echo "$template_answer" | jq \
                --arg ag "$input_actionGroup" \
                --arg fn "$input_function" \
                --arg bd "$RESULT" \
                '.response.actionGroup = $ag |
        .response.function = $fn |
        .response.functionResponse.responseBody.TEXT.body = $bd')

        else

            updated_json=$(echo "$template_answer" | jq \
                --arg ag "$input_actionGroup" \
                --arg fn "$input_function" \
                --arg bd "$RESULT" \
                --arg responseState "REPROMPT" \
                '.response.actionGroup = $ag |
        .response.function = $fn |
        .response.functionResponse.responseState = $responseState |
        .response.functionResponse.responseBody.TEXT.body = $bd')

        fi
    fi

    # Output the JSON response
    echo "$updated_json"

}
