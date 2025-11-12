#!/usr/bin/env python3
"""
src/generate_plone_addon/generator.py

Generatore di addon Plone a partire da una directory template_files.
Sostituisce placeholder {{key}} sia nei nomi di file/cartelle sia nel contenuto dei file testuali.
Rileva automaticamente i file testuali (UTF-8/ASCII) senza basarsi su estensioni.
"""

from pathlib import Path
import shutil
import argparse
import sys
from typing import Dict


# ------------------------------------------------------------
# Funzioni di utilità
# ------------------------------------------------------------

def replace_placeholders(text: str, context: Dict[str, str]) -> str:
    """Sostituisce tutti i placeholder {{key}} presenti in text usando context."""
    for k, v in context.items():
        text = text.replace(f"{{{{{k}}}}}", v)
    return text


def is_text_file(path: Path, sample_size: int = 2048) -> bool:
    """
    Rileva automaticamente se un file è testuale leggendo i primi bytes.
    Restituisce True se è probabilmente testo UTF-8 o ASCII, False se binario.
    """
    try:
        with path.open("rb") as f:
            chunk = f.read(sample_size)
        if b"\x00" in chunk:  # byte nulli tipici dei binari
            return False
        try:
            chunk.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False
    except Exception:
        # In caso di errore di lettura, consideralo binario per sicurezza
        return False


def render_template_file(src: Path, dest: Path, context: Dict[str, str], dry_run: bool = False) -> None:
    """Legge src come testo UTF-8, sostituisce placeholder e scrive dest. Preserva permessi."""
    content = src.read_text(encoding="utf-8")
    for k, v in context.items():
        content = content.replace(f"{{{{{k}}}}}", v)
    if not dry_run:
        dest.write_text(content, encoding="utf-8")
        try:
            shutil.copymode(src, dest)
        except Exception:
            pass


def copy_binary(src: Path, dest: Path, dry_run: bool = False) -> None:
    """Copia file binario preservando metadata di base."""
    if not dry_run:
        shutil.copy2(src, dest)


def get_template_dir() -> Path:
    """
    Restituisce la directory 'template_files' relativa al package.
    (Assume che template_files sia dentro lo stesso package: src/generate_plone_addon/template_files)
    """
    return Path(__file__).resolve().parent / "template_files"


def build_context(addon_name: str) -> Dict[str, str]:
    """Costruisce il context a partire da addon_name (namespace.module)."""
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


# ------------------------------------------------------------
# Funzione principale di copia template
# ------------------------------------------------------------

def copy_template(template_dir: Path, dest_base: Path, context: Dict[str, str],
                  dry_run: bool = False, verbose: bool = False) -> None:
    """
    Copia ricorsivamente template_dir in dest_base/<package_name>,
    sostituendo placeholder nei nomi e nei contenuti.
    """
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory non trovata: {template_dir}")

    for src in sorted(template_dir.rglob("*")):
        rel = src.relative_to(template_dir)
        # Sostituisci placeholder in ogni componente del percorso
        new_parts = [replace_placeholders(part, context) for part in rel.parts]
        target = dest_base.joinpath(*new_parts)

        if src.is_dir():
            if verbose:
                print(f"[DIR]  {src} -> {target}")
            if not dry_run:
                target.mkdir(parents=True, exist_ok=True)
            continue

        # Assicurati che la directory target esista
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)

        # Determina se è testo o binario
        treat_as_text = is_text_file(src)

        if treat_as_text:
            if verbose:
                print(f"[TEX]  {src} -> {target}")
            render_template_file(src, target, context, dry_run=dry_run)
        else:
            if verbose:
                print(f"[BIN]  {src} -> {target}")
            copy_binary(src, target, dry_run=dry_run)


# ------------------------------------------------------------
# Entry point CLI
# ------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Genera un addon Plone da template_files.")
    p.add_argument("addon_name", nargs="?", help="Nome addon (es. guanda.site). Se omesso verrà chiesto interattivamente.")
    p.add_argument("--dest", "-d", help="Directory di destinazione (default: cwd).")
    p.add_argument("--dry-run", action="store_true", help="Non scrive nulla, mostra cosa farebbe.")
    p.add_argument("-v", "--verbose", action="store_true", help="Output verboso.")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    if args.addon_name:
        addon_name = args.addon_name.strip()
    else:
        addon_name = input("Nome addon (es. guanda.site): ").strip()

    if "." not in addon_name:
        print("Errore: usare formato namespace.modulo (es. guanda.site)")
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
        copy_template(template_dir, dest_dir, context, dry_run=args.dry_run, verbose=args.verbose)
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
