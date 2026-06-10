from rich import print as rprint
from pygame import mixer

mixer.init()
mixer.set_num_channels(500)

sounds = {
    "startup": mixer.Sound("sound/st.wav"),
    "tik": mixer.Sound("sound/up.wav"),
    "tok": mixer.Sound("sound/dn.wav"),
    "error": mixer.Sound("sound/er.wav"),
    "exit": mixer.Sound("sound/xt.wav")
}

# Prepare channel objects (user-facing channels 1..5 -> pygame channels 0..4)
channels = {i: mixer.Channel(i - 1) for i in range(1, 6)}
# Tok should rotate across channels 2,3,4 (user numbering)
_tok_channel_nums = [2, 3, 4]
_tok_channel_objs = [channels[n] for n in _tok_channel_nums]
_tok_next = 0

def play_on_channel(key: str) -> None:
    """Play a sound on the configured channel(s).

    - 'startup' -> channel 5
    - 'tik'     -> channel 1
    - 'tok'     -> round-robin channels 2,3,4
    """
    global _tok_next
    if key == "startup":
        channels[5].play(sounds["startup"])
    elif key == "tik":
        channels[1].play(sounds["tik"])
    elif key == "tok":
        ch = _tok_channel_objs[_tok_next]
        ch.play(sounds["tok"])
        _tok_next = (_tok_next + 1) % len(_tok_channel_objs)
    else:
        # fallback: play directly if key exists
        s = sounds.get(key)
        if s is not None:
            s.play()

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
    while b <= 3:
        print("#", end="", flush=True)
        if (b % 4) == 0:
            play_on_channel("tik")
        else:
            play_on_channel("tok")
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

def check_for_continuous_bps(numerator: int, denominator: int, max_digits: int = 200) -> str:
    """Return a decimal representation of numerator/denominator.

    If the decimal terminates, return the exact decimal (no trailing dots).
    If it repeats, return the integer part, the non-repeating fraction digits,
    then the first repeating block once followed by '...'.

    Examples:
    - 60/4 -> '15'
    - 60/7 -> '8.571428...'
    - 1/3  -> '0.3...'
    """
    if denominator == 0:
        raise ZeroDivisionError("Denominator cannot be zero")

    # integer part
    integer_part = numerator // denominator
    remainder = numerator % denominator

    if remainder == 0:
        return str(integer_part)

    digits = []
    rem_pos = {}
    pos = 0

    while remainder != 0 and remainder not in rem_pos and pos < max_digits:
        rem_pos[remainder] = pos
        remainder *= 10
        digit = remainder // denominator
        digits.append(str(digit))
        remainder = remainder % denominator
        pos += 1

    if remainder == 0:
        # terminating decimal
        return f"{integer_part}.{''.join(digits)}"
    else:
        # repeating decimal; show first repeating block then '...'
        repeat_start = rem_pos[remainder]
        non_repeat = ''.join(digits[:repeat_start])
        repeat = ''.join(digits[repeat_start:])
        if non_repeat:
            return f"{integer_part}.{non_repeat}{repeat}..."
        else:
            return f"{integer_part}.{repeat}..."


if __name__ == "__main__":
    play_on_channel("startup")
    print("Hey! This program has sounds!")
    clear_screen()
    while True:
        try:
            raw = input("insert your BPM/Tempo (only numbers allowed): ")
            a = int(raw)
            if a < 0:
                sounds["error"].play()
                raise ValueError("BPM/Tempo cannot be negative")
            if a == 0:
                sounds["error"].play()
                print("BPM/Tempo cannot be zero, please try again.")
                continue

            p = "are" if a > 1 else "is"
            b = a / 60
            # Represent seconds-per-beat as a rational 60/a to detect repeating decimals
            
            seconds_repr = check_for_continuous_bps(60, a)
            rprint(f"Your BPM/Tempo is: [blue]{a}[/blue], meaning for every second, there are [green]{b}[/green] beats, and in between every beat, there {p} [violet]{seconds_repr}[/violet] seconds.")
            print("here is a visual example of the BPM/Tempo:")
            while True:
                visual_bps(b)

        except ValueError as e:
            msg = str(e)
            if "negative" in msg:
                sounds["error"].play()
                print(msg)
            else:
                sounds["error"].play()
                print("Invalid input, please enter a number.")
            continue
        except KeyboardInterrupt:
            sounds["exit"].play()
            print("\nExiting.")
            break