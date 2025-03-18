import os
import sys
import traceback
import datetime

def write_error_log(error, trace):
    """Write error details to the log file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_content = f"""
=== GLFS Error Log ===
Time: {timestamp}
Error: {str(error)}

=== Stack Trace ===
{trace}

=== System Info ===
Python Version: {sys.version}
Platform: {sys.platform}
Working Directory: {os.getcwd()}
"""
    
    with open("error_log.txt", "w", encoding='utf-8') as f:
        f.write(log_content)

def main():
    try:
        print("Starting GLFS in debug mode...")
        import src.main
    except Exception as e:
        error_trace = traceback.format_exc()
        write_error_log(e, error_trace)
        
        print("\nError running GLFS:")
        print(f"  {str(e)}")
        print("\nPossible solutions:")
        print("1. Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        print("2. Install WebView2 Runtime from:")
        print("   https://developer.microsoft.com/en-us/microsoft-edge/webview2/")
        print("3. Check error_log.txt for detailed error information")
        print("\nPress Enter to exit...")
        input()

if __name__ == "__main__":
    main()
