#!/usr/bin/env python3

from pathlib import Path
import shutil
import argparse
import sys
from typing import Dict


def replace_placeholders(text: str, context: Dict[str, str]) -> str:
    for key, value in context.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def is_text_file(path: Path, sample_size: int = 2048) -> bool:
    try:
        with path.open("rb") as f:
            chunk = f.read(sample_size)

        if b"\x00" in chunk:
            return False

        try:
            chunk.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False
    except Exception:
        return False


def render_template_file(src: Path, dest: Path, context: Dict[str, str], dry_run: bool = False) -> None:
    content = src.read_text(encoding = "utf-8")

    for key, value in context.items():
        content = content.replace(f"{{{{{key}}}}}", value)

    if not dry_run:
        dest.write_text(content, encoding = "utf-8")

        try:
            shutil.copymode(src, dest)
        except Exception:
            pass


def copy_binary(src: Path, dest: Path, dry_run: bool = False) -> None:
    if not dry_run:
        shutil.copy2(src, dest)


def get_template_dir() -> Path:
    mode = sys.argv[1] if len(sys.argv) > 1 else "addon"

    if mode not in ("addon", "theme"):
        print(f"Modalità sconosciuta: {mode}")
        print("Usa: generate_plone_addon [addon|theme]")
        sys.exit(1)

    template_name = "template_addon" if mode == "addon" else "template_theme"
    template_dir = Path(__file__).resolve().parent / template_name

    return template_dir


def build_context(addon_name: str) -> Dict[str, str]:
    namespace, module = addon_name.split(".", 1)

    layer_name = "".join(part.capitalize() for part in addon_name.split("."))

    layer_name_uppercase = "_".join(part.upper() for part in addon_name.split("."))

    return {
        "namespace": namespace,
        "module": module,
        "package_layer": layer_name,
        "package_name": addon_name,
        "package_layer_uppercase": layer_name_uppercase,
    }


def copy_template(template_dir: Path, dest_base: Path, context: Dict[str, str], dry_run: bool = False, verbose: bool = False) -> None:
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory non trovata: {template_dir}")

    for src in sorted(template_dir.rglob("*")):
        rel = src.relative_to(template_dir)

        new_parts = [replace_placeholders(part, context) for part in rel.parts]
        target = dest_base.joinpath(*new_parts)

        if src.is_dir():
            if verbose:
                print(f"[DIR]  {src} -> {target}")
            if not dry_run:
                target.mkdir(parents = True, exist_ok = True)
            continue

        if not dry_run:
            target.parent.mkdir(parents = True, exist_ok = True)

        treat_as_text = is_text_file(src)

        if treat_as_text:
            if verbose:
                print(f"[TEXT] {src} -> {target}")
            render_template_file(src, target, context, dry_run = dry_run)
        else:
            if verbose:
                print(f"[BIN]  {src} -> {target}")
            copy_binary(src, target, dry_run = dry_run)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description = "Genera un addon Plone da template."
    )

    parser.add_argument(
        "addon_name",
        nargs = "?",
        help = "Nome addon (es. plone.site)."
    )
    parser.add_argument(
        "--dest", "-d",
        help = "Directory di destinazione (default: cwd)."
    )
    parser.add_argument(
        "--dry-run",
        action = "store_true",
        help = "Non scrive nulla, mostra cosa farebbe."
    )
    parser.add_argument(
        "-v", "--verbose",
        action = "store_true",
        help = "Output verboso."
    )
    parser.add_argument(
        "--name",
        help = "Nome del pacchetto da creare"
    )

    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    addon_name = args.name or args.addon_name

    if not addon_name:
        print("Errore: specificare un nome addon")
        return 2

    addon_name = addon_name.strip()

    if "." not in addon_name:
        print("Errore: usare formato namespace.modulo (es. plone.site)")
        return 2

    dest_base = Path(args.dest).resolve() if args.dest else Path.cwd().resolve()
    dest_dir = dest_base / addon_name

    context = build_context(addon_name)
    template_dir = get_template_dir()

    if args.verbose:
        print(f"Template dir: {template_dir}")
        print(f"Dest dir:     {dest_dir}")
        print(f"Context:      {context}")

    try:
        copy_template(
            template_dir,
            dest_dir,
            context,
            dry_run = args.dry_run,
            verbose = args.verbose
        )
    except FileNotFoundError as e:
        print(f"ERRORE: {e}")
        return 1
    except Exception as e:
        print(f"Errore in fase di copia: {e}")
        return 1

    if args.dry_run:
        print("Dry run completato. Nessun file è stato scritto.")
    else:
        print(f"Addon '{addon_name}' generato in {dest_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
