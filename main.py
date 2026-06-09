from rich import print as rprint
def clear_screen():
    import os
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def clearlastline():
    import sys
    import shutil
    try:
        width = shutil.get_terminal_size().columns
    except Exception:
        width = 80
    # Move to start of the current line, overwrite it with spaces, then return
    sys.stdout.write('\r' + ' ' * width + '\r')
    sys.stdout.flush()

def key_pressed():
    import sys
    import os
    if os.name == 'nt':
        import msvcrt
        return msvcrt.kbhit()
    else:
        import select
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(dr)

def consume_key():
    import sys
    import os
    if os.name == 'nt':
        import msvcrt
        while msvcrt.kbhit():
            try:
                msvcrt.getch()
            except Exception:
                break
    else:
        try:
            import termios
            import tty
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
        except Exception:
            # Fallback: attempt a non-blocking read
            try:
                import sys
                sys.stdin.read()
            except Exception:
                pass

def visual_bps(bps):
    import time
    b = 0
    # For better responsiveness to keypresses, sleep in short intervals
    while b <= 3:
        print("#", end="", flush=True)
        sleep_total = 1 / bps if bps != 0 else 0
        interval = 0.05
        elapsed = 0.0
        start = time.time()
        while elapsed < sleep_total:
            if key_pressed():
                consume_key()
                quit()
            to_sleep = min(interval, sleep_total - elapsed)
            if to_sleep > 0:
                time.sleep(to_sleep)
            elapsed = time.time() - start
        b += 1
    clearlastline()

if __name__ == "__main__":
    clear_screen()
    while True:
        a = int(input("insert your BPM/Tempo (only numbers allowed): "))
        try:
            try:
                p = "are" if a != 1 else "is"
                b = a / 60
                rprint(f"Your BPM/Tempo is: [blue]{a}[/blue], meaning for every second, there are [green]{b}[/green] beats, and in between every beat, there {p} [violet]{1/b}[/violet] seconds.")
                print("here is a visual example of the BPM/Tempo:")
                while True:
                    visual_bps(b)
            except ZeroDivisionError:
                print("BPM/Tempo cannot be zero, please try again.")  
        except ValueError:
            print("Invalid input, please enter a number.")