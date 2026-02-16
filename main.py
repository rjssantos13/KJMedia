def main():
    """Entry point that redirects to the actual application"""
    import sys
    import os

    # Add the project root to Python path for imports
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from src.kjmedia.main import main as app_main

    app_main()


if __name__ == "__main__":
    main()
