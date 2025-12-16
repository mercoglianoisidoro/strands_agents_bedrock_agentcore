"""Allow running the package with python -m local_agents or python local_agents"""
from local_agents.cli import run_main

if __name__ == "__main__":
    try:
        run_main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import sys
        sys.exit(1)

