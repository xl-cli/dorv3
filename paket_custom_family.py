import json
from api_request import send_api_request, get_family
from auth_helper import AuthInstance
from ui import (
    clear_screen,
    show_package_details,
    pause,
    console,
    _c,
    RICH_OK,
    _print_full_width_panel,
    _print_centered_panel
)

try:
    from rich.table import Table
    from rich.prompt import Prompt
    from rich.box import ROUNDED
except ImportError:
    pass

def get_packages_by_family(family_code: str, is_enterprise: bool = False):
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    if not tokens:
        if RICH_OK:
            console.print(f"[{_c('text_err')}]No active user tokens found.[/]")
        else:
            print("No active user tokens found.")
        pause()
        return None
        
    packages = []
    
    data = get_family(api_key, tokens, family_code, is_enterprise)
    if not data:
        if RICH_OK:
            console.print(f"[{_c('text_err')}]Failed to load family data.[/]")
        else:
            print("Failed to load family data.")
        pause()
        return None
    
    in_package_menu = True
    while in_package_menu:
        clear_screen()
        family_name = data['package_family']["name"] if data.get('package_family') else "Tidak diketahui"
        package_variants = data.get("package_variants", [])

        if RICH_OK:
            panel_title = f"[{_c('text_title')}]Family Name:[/] [{_c('text_ok')}]{family_name}[/{_c('text_ok')}]"
            _print_full_width_panel(
                panel_title,
                border_style=_c("border_info"),
                box=ROUNDED
            )
            table = Table(
                title=f"[{_c('text_title')}]Paket Tersedia[/]", show_header=True,
                header_style=_c("text_sub"), box=ROUNDED, expand=True
            )
            table.add_column("No", justify="right", style=_c("text_number"))
            table.add_column("Nama Paket", style=_c("text_body"))
            table.add_column("Harga", style=_c("text_money"))
        else:
            print("--------------------------")
            print(f"Family Name: {family_name}")
            print("Paket Tersedia")
            print("--------------------------")
        
        packages.clear()
        option_number = 1
        variant_number = 1
        for variant in package_variants:
            variant_name = variant.get("name", "Tidak diketahui")
            if RICH_OK:
                table.add_row("", f"[{_c('text_sub')}]Variant {variant_number}: {variant_name}[/]". "")
            else:
                print(f" Variant {variant_number}: {variant_name}")
            for option in variant.get("package_options", []):
                option_name = option.get("name", "Tidak diketahui")
                option_price = option.get("price", 0)
                option_code = option.get("package_option_code", "")
                formatted_price = f"{int(option_price):,}"  # Format ribuan pakai koma
                packages.append({
                    "number": option_number,
                    "name": option_name,
                    "price": formatted_price,
                    "code": option_code
                })
                if RICH_OK:
                    table.add_row(
                        str(option_number), option_name, f"Rp {formatted_price}"
                    )
                else:
                    print(f"{option_number}. {option_name} - Rp {formatted_price}")
                option_number += 1
            variant_number += 1

        if RICH_OK:
            table.add_row("00", f"[{_c('text_err')}]Kembali ke menu sebelumnya[/]", "")
            _print_full_width_panel(
                table,
                title=f"[{_c('text_title')}]Daftar Paket Family[/]",
                border_style=_c("border_info"),
                box=ROUNDED
            )
            pkg_choice = Prompt.ask(f"[{_c('text_sub')}]Pilih paket (nomor)").strip()
        else:
            print("00. Kembali ke menu sebelumnya")
            pkg_choice = input("Pilih paket (nomor): ").strip()
        if pkg_choice == "00":
            in_package_menu = False
            return None
        if not pkg_choice.isdigit():
            if RICH_OK:
                console.print(f"[{_c('text_err')}]Masukan harus berupa angka.[/]")
            else:
                print("Masukan harus berupa angka.")
            pause()
            continue

        selected_pkg = next((p for p in packages if p["number"] == int(pkg_choice)), None)
        if not selected_pkg:
            if RICH_OK:
                console.print(f"[{_c('text_err')}]Paket tidak ditemukan. Silakan masukan nomor yang benar.[/]")
            else:
                print("Paket tidak ditemukan. Silakan masukan nomor yang benar.")
            pause()
            continue
        
        is_done = show_package_details(api_key, tokens, selected_pkg["code"])
        if is_done:
            in_package_menu = False
            return None

    return packages
