import argparse
import json
import queue
import sys
import urllib.request
import zipfile
from pathlib import Path


def _missing_dependency_message(module_name: str) -> str:
    return (
        f"Missing Python module: {module_name}\n"
        "Install the local test dependencies with:\n"
        "  python -m pip install vosk sounddevice\n"
    )


try:
    import sounddevice as sd
except ModuleNotFoundError:
    print(_missing_dependency_message("sounddevice"), file=sys.stderr)
    raise SystemExit(1)

try:
    from vosk import KaldiRecognizer, Model, SetLogLevel
except ModuleNotFoundError:
    print(_missing_dependency_message("vosk"), file=sys.stderr)
    raise SystemExit(1)


SetLogLevel(-1)
VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Quick local microphone test for the Vosk model."
    )
    parser.add_argument(
        "--model",
        default="vosk-model",
        help="Path to the Vosk model directory. Default: ./vosk-model",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Input device id or substring of the device name.",
    )
    parser.add_argument(
        "--samplerate",
        type=float,
        default=None,
        help="Override microphone sample rate. Defaults to the device default.",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="Print available audio devices and exit.",
    )
    parser.add_argument(
        "--blocksize",
        type=int,
        default=8000,
        help="Frames per callback block. Default: 8000",
    )
    return parser.parse_args()


def resolve_device(device_arg):
    if device_arg is None:
        return None

    try:
        return int(device_arg)
    except ValueError:
        pass

    devices = sd.query_devices()
    needle = device_arg.lower()
    for index, dev in enumerate(devices):
        if dev["max_input_channels"] <= 0:
            continue
        if needle in dev["name"].lower():
            return index

    raise SystemExit(f"Could not find an input device matching: {device_arg}")


def default_samplerate_for(device_index):
    if device_index is None:
        default_input = sd.default.device[0]
        if default_input is None or default_input < 0:
            raise SystemExit(
                "No default input device found. Run with --list-devices first."
            )
        device_index = default_input

    info = sd.query_devices(device_index, "input")
    return int(info["default_samplerate"])


def print_devices():
    for index, dev in enumerate(sd.query_devices()):
        io_kind = []
        if dev["max_input_channels"] > 0:
            io_kind.append("input")
        if dev["max_output_channels"] > 0:
            io_kind.append("output")
        label = "/".join(io_kind) if io_kind else "n/a"
        print(
            f"[{index}] {dev['name']} | {label} | "
            f"default_sr={dev['default_samplerate']}"
        )


def ensure_model(model_path: Path):
    if model_path.exists():
        return model_path

    print(f"Model directory not found: {model_path}")
    print("Downloading Vosk small English model (~40 MB)...")

    zip_path = model_path.with_suffix(".zip")
    urllib.request.urlretrieve(VOSK_MODEL_URL, zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(model_path.parent)

    extracted_name = VOSK_MODEL_URL.split("/")[-1].replace(".zip", "")
    extracted_path = model_path.parent / extracted_name
    if extracted_path.exists() and extracted_path != model_path:
        extracted_path.rename(model_path)

    zip_path.unlink(missing_ok=True)
    print(f"Model ready at: {model_path}")
    return model_path


def main():
    args = parse_args()

    if args.list_devices:
        print_devices()
        return

    model_path = ensure_model(Path(args.model))
    device_index = resolve_device(args.device)
    samplerate = int(args.samplerate or default_samplerate_for(device_index))

    print(f"Loading Vosk model from: {model_path}")
    model = Model(str(model_path))
    recognizer = KaldiRecognizer(model, samplerate)

    q = queue.Queue()

    def callback(indata, _frames, _time_info, status):
        if status:
            print(f"[audio] {status}", file=sys.stderr)
        q.put(bytes(indata))

    print("Starting microphone test.")
    print("Speak naturally. Press Ctrl+C to stop.")
    print(f"Input device: {device_index if device_index is not None else 'default'}")
    print(f"Sample rate: {samplerate}")

    with sd.RawInputStream(
        samplerate=samplerate,
        blocksize=args.blocksize,
        device=device_index,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        try:
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        print(f"[final] {text}")
                else:
                    partial = json.loads(recognizer.PartialResult())
                    text = partial.get("partial", "").strip()
                    if text:
                        print(f"[partial] {text}", end="\r", flush=True)
        except KeyboardInterrupt:
            print()
            final = json.loads(recognizer.FinalResult())
            text = final.get("text", "").strip()
            if text:
                print(f"[exit-final] {text}")
            print("Stopped.")


if __name__ == "__main__":
    main()
