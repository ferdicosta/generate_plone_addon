import os
import shutil

TEXT_EXT = {".py", ".zcml", ".cfg", ".pt", ".xml", ".txt", ".rst", ".md", ".po", ".pot", ".sh"}

def render_template_file(src_file, dest_file, context):
    with open(src_file, "r", encoding="utf-8") as f:
        content = f.read()
    # Sostituisci tutti i placeholders {{key}} con i valori
    for k, v in context.items():
        content = content.replace(f"{{{{{k}}}}}", v)
    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(content)


def replace_placeholders(text, context):
    for k, v in context.items():
        text = text.replace(f"{{{{{k}}}}}", v)
    return text

def copy_template(template_dir, dest_dir, context):
    for root, dirs, files in os.walk(template_dir):
        rel_path = os.path.relpath(root, template_dir)
        # Sostituisci placeholders nei percorsi
        rel_path = replace_placeholders(rel_path, context)
        target_root = os.path.join(dest_dir, rel_path)
        os.makedirs(target_root, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(target_root, file)

            ext = os.path.splitext(file)[1].lower()

            if ext in TEXT_EXT:
                render_template_file(src_file, dest_file, context)
            else:
                shutil.copy2(src_file, dest_file)


def main():
    addon_name = input("Nome addon (es. guanda.site): ").strip()

    if "." not in addon_name:
        print("Errore: usare formato namespace.modulo (es. guanda.site)")
        return

    namespace, module = addon_name.split(".")
    # Costruisco il nome del layer per Plone
    # es. guanda.site -> GuandaSiteLayer
    layer_name = "".join([p.capitalize() for p in addon_name.split(".")])
    layer_name_uppercase = "_".join([p.upper() for p in addon_name.split(".")])

    context = {
        "namespace": namespace,
        "module": module,
        "package_layer": layer_name,
        "package_name": addon_name,
        "package_layer_uppercase": layer_name_uppercase,
    }

    dest_dir = os.path.join("", addon_name)
    copy_template("template_files", dest_dir, context)

    print(f"Addon '{addon_name}' generato in {dest_dir}")
    print("Ora puoi buildarlo con: python -m build")
    print("E installarlo: pip install dist/<nome-pacchetto>.whl")


if __name__ == "__main__":
    main()
