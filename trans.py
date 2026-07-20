import json
import sys
import typing

from argparse import ArgumentParser, RawDescriptionHelpFormatter, Namespace
from json import JSONDecodeError
from pathlib import Path


def xep_tu_dien(d: dict) -> dict:
    """
    Sắp xếp từ điển theo khóa
    """
    def sap_xep(tu_khoa: typing.ItemsView) -> tuple:
        khoa: str | int = tu_khoa[0]
        try:
            return (0, int(khoa))
        except ValueError:
            return (1, khoa)

    return dict(sorted(d.items(), key=sap_xep))


def hop_nhat_ds(a: list, b: list, khoa: str) -> list:
    """
    Hợp nhất 2 danh sách, nếu có phần tử trùng khóa thì chọn cái sau (danh sách B)
    """
    du_lieu: dict = {}
    ma_moi: list = []
    for mon in b:
        du_lieu[mon[khoa]] = mon

    for mon in a:
        if mon[khoa] not in du_lieu:
            du_lieu[mon[khoa]] = mon
            ma_moi.append(mon[khoa])

    if ma_moi:
        print('Các định danh mới:')
        for mon in ma_moi:
            print(f'- {mon}')

        print()

    du_lieu = xep_tu_dien(du_lieu)
    return list(du_lieu.values())


def hop_nhat_dict(a: dict, b: dict, khoa: str) -> dict:
    """
    Hợp nhất từ điển con
    """
    # nếu từ khóa trong từ điển đích không phải kiểu dữ liệu từ điển thì lấy từ khóa của từ điển nguồn
    if not isinstance(b[khoa], dict):
        return a[khoa]

    du_lieu: dict = {}
    khoa_moi: list = []
    khoa_cu: list = []
    for khoa_con in b[khoa]:
        if khoa_con in a[khoa]:
            du_lieu[khoa_con] = b[khoa][khoa_con]
        else:
            khoa_cu.append(b[khoa])

    for khoa_con in a[khoa]:
        if khoa_con not in du_lieu:
            du_lieu[khoa_con] = a[khoa][khoa_con]
            khoa_moi.append(khoa_con)

    if khoa_moi or khoa_cu:
        print(f'  Từ khóa {khoa}')
        if khoa_moi:
            print('    Các từ khóa mới:')
            for mon in khoa_moi:
                print(f'    - {mon}')

            print()

        if khoa_cu:
            print('    Các từ khóa cũ:')
            for mon in khoa_cu:
                print(f'    - {mon}')

            print()

    return xep_tu_dien(du_lieu)


def so_sanh_dict(a: dict, b: dict) -> dict:
    """
    Hợp nhất 2 từ điển, nếu có từ khóa trùng thì chọn cái sau (từ điển B)
    """
    c: dict = {}
    khoa_moi: list = []
    for khoa in b:
        if khoa in a:
            if isinstance(a[khoa], dict):
                c[khoa] = hop_nhat_dict(a, b, khoa)
            else:
                c[khoa] = b[khoa]

    for khoa in a:
        if khoa not in c:
            c[khoa] = a[khoa]
            khoa_moi.append(khoa)

    if khoa_moi:
        print('Các từ khóa mới:')
        for mon in khoa_moi:
            print(f'- {mon!r}')

        print()

    return xep_tu_dien(c)


def so_sanh_almanac(thu_muc_a: Path, thu_muc_b: Path) -> None:
    tep_moi: list = []
    ds_json: tuple = tuple(thu_muc_b.glob('*.json'))
    if ds_json:
        duong_dan: str = f'{thu_muc_goc}/c/Almanac'
        Path(duong_dan).mkdir(parents=True, exist_ok=True)
        for mon in ds_json:
            tep_b: str = str(mon)
            tam: str = tep_b.rsplit('/', 1)
            tep_json: str = tam[1]
            tep_a = Path(thu_muc_a, tep_json)

            # tệp có trong ngôn ngữ nguồn nhưng không có trong ngôn ngữ đích
            if not tep_a.is_file():
                tep_moi.append(tep_json)
                continue

            with open(tep_a, encoding='utf-8') as f:
                du_lieu_a: dict = json.load(f)

            with open(tep_b, encoding='utf-8') as f:
                du_lieu_b: dict = json.load(f)

            tep_c: str = f'{duong_dan}/{tep_json}'
            print(f'+ {tep_c}')
            if tep_json == 'LawnStringsTranslate.json':
                muc: str = 'plants'
                du_lieu: list = hop_nhat_ds(du_lieu_b.get(muc, []), du_lieu_a.get(muc, []), 'seedType')
                with open(tep_c, 'w', encoding='utf-8') as f:
                    json.dump({muc: du_lieu}, f, ensure_ascii=False, indent=2)

            elif tep_json == 'ZombieStringsTranslate.json':
                muc: str = 'zombies'
                du_lieu: list = hop_nhat_ds(du_lieu_b.get(muc, []), du_lieu_a.get(muc, []), 'theZombieType')
                with open(tep_c, 'w', encoding='utf-8') as f:
                    json.dump({muc: du_lieu}, f, ensure_ascii=False, indent=2)

            else:
                du_lieu: dict = so_sanh_dict(du_lieu_b, du_lieu_a)
                with open(tep_c, 'w', encoding='utf-8') as f:
                    json.dump(du_lieu, f, ensure_ascii=False, indent=2)

            print()

    if tep_moi:
        print('Các tệp mới:')
        for tep in tep_moi:
            print(f'- {tep}')

        print()


def so_sanh_strings(thu_muc_a: Path, thu_muc_b: Path) -> None:
    tep_moi: list = []
    tep_bom: list = []
    ds_json: tuple = tuple(thu_muc_b.glob('*.json'))
    if ds_json:
        duong_dan: str = f'{thu_muc_goc}/c/Strings'
        Path(duong_dan).mkdir(parents=True, exist_ok=True)
        for mon in ds_json:
            tep_b: str = str(mon)
            tam: str = tep_b.rsplit('/', 1)
            tep_json: str = tam[1]
            tep_a = Path(thu_muc_a, tep_json)

            # tệp có trong ngôn ngữ nguồn nhưng không có trong ngôn ngữ đích
            if not tep_a.is_file():
                tep_moi.append(tep_json)
                continue

            try:
                with open(tep_a, encoding='utf-8') as f:
                    du_lieu_a: dict = json.load(f)
            except JSONDecodeError:
                tep_bom.append(tep_a)
                with open(tep_a, encoding='utf-8-sig') as f:
                    du_lieu_a: dict = json.load(f)

            try:
                with open(tep_b, encoding='utf-8') as f:
                    du_lieu_b: dict = json.load(f)
            except JSONDecodeError:
                tep_bom.append(tep_b)
                with open(tep_b, encoding='utf-8-sig') as f:
                    du_lieu_b: dict = json.load(f)

            tep_c: str = f'{duong_dan}/{tep_json}'
            print(f'+ {tep_c}')

            du_lieu: dict = so_sanh_dict(du_lieu_b, du_lieu_a)
            with open(tep_c, 'w', encoding='utf-8') as f:
                json.dump(du_lieu, f, ensure_ascii=False, indent=2)

            print()

    if tep_moi:
        print('Các tệp mới:')
        for tep in tep_moi:
            print(f'- {tep}')

        print()

    if tep_bom:
        vang: str = '\x1b[1;33m'
        dat_lai: str = '\x1b[0m'
        print(f'{vang}Các tệp BOM:{dat_lai}')
        for tep in tep_bom:
            print(f'- {tep}')

        print()


if __name__ == '__main__':
    tap_lenh = Path(__file__)
    thu_muc_goc = tap_lenh.parent
    parser = ArgumentParser(
        description='So sánh dữ liệu dịch thuật',
        epilog='Bản quyền © 2026 Vũ Đắc Hoàng Ân',
        formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('-v', '--version', action='version', version='So sánh Json 1.0.0')
    parser.add_argument('l', help='Đường dẫn thư mục PVZF-Translation/PvZ_Fusion_Translator/Localization/')
    parser.add_argument('a', nargs='?', default='Vietnamese', help='Ngôn ngữ đích (mặc định: tiếng Việt)')
    parser.add_argument('b', nargs='?', default='English', help='Ngôn ngữ nguồn (mặc định: tiếng Anh)')
    args: Namespace = parser.parse_args()

    tam = Path(args.l)
    dia_phuong = tam.resolve()
    ds_phan_he: tuple = ('Almanac', 'Strings')
    if not dia_phuong.is_dir():
        print(f'Thư mục {dia_phuong} không tồn tại')
        sys.exit(1)

    for phan_he in ds_phan_he:
        print(f'Mô đun {phan_he}')
        thu_muc_a = Path(dia_phuong, args.a, phan_he)
        if not thu_muc_a.is_dir():
            print(f'Thư mục {thu_muc_a} không tồn tại')
            sys.exit(1)

        thu_muc_b = Path(dia_phuong, args.b, phan_he)
        if not thu_muc_b.is_dir():
            print(f'Thư mục {thu_muc_b} không tồn tại')
            sys.exit(1)

        if phan_he == 'Almanac':
            so_sanh_almanac(thu_muc_a, thu_muc_b)
        elif phan_he == 'Strings':
            so_sanh_strings(thu_muc_a, thu_muc_b)

    print('Xong')
