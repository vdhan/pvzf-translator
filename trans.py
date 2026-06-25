import json
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter, Namespace
from pathlib import Path


def sap_xep_dict(d: dict) -> dict:
    """
    Sắp xếp từ điển theo khóa
    """
    return dict(sorted(d.items()))


def hop_nhat_ds(a: list, b: list, khoa: str) -> list:
    """
    Hợp nhất 2 danh sách, nếu có phần tử trùng khóa thì chọn cái sau (danh sách B)
    """
    tam: dict = {}
    for mon in a:
        tam[mon[khoa]] = mon

    for mon in b:
        tam[mon[khoa]] = mon

    tam = sap_xep_dict(tam)
    return list(tam.values())


def hop_nhat_dict(a: dict, b: dict) -> dict:
    """
    Hợp nhất 2 từ điển, nếu có từ khóa trùng thì chọn cái sau (từ điển B)
    """
    tam: dict = {}
    khoa_moi: list = []
    for khoa in a:
        if khoa in b:
            tam[khoa] = a[khoa]

    for khoa in b:
        if khoa not in tam:
            tam[khoa] = b[khoa]
            khoa_moi.append(khoa)

    if khoa_moi:
        print('Các từ khóa mới:')
        for khoa in khoa_moi:
            print(f'- {khoa}')

    return tam


def so_sanh_almanac() -> None:
    print('Mô đun Almanac')
    phan_he = 'Almanac'
    thu_muc_a = Path(dia_phuong, args.a, phan_he)
    if not thu_muc_a.is_dir():
        print(f'Thư mục {thu_muc_a} không tồn tại')
        sys.exit(1)

    thu_muc_b = Path(dia_phuong, args.b, phan_he)
    if not thu_muc_b.is_dir():
        print(f'Thư mục {thu_muc_b} không tồn tại')
        sys.exit(1)

    tep_moi: list = []
    ds_json: tuple = tuple(thu_muc_b.glob('*.json'))
    if ds_json:
        almanac: str = f'{thu_muc_goc}/c/{phan_he}'
        Path(almanac).mkdir(parents=True, exist_ok=True)
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

            tep_c: str = f'{almanac}/{tep_json}'
            print(f'+ {tep_c}')
            if tep_json == 'LawnStringsTranslate.json':
                muc: str = 'plants'
                du_lieu: list = hop_nhat_ds(du_lieu_b.get(muc, []), du_lieu_a.get(muc, []), 'seedType')
                with open(tep_c, 'w', encoding='utf-8') as f:
                    json.dump({muc: du_lieu}, f, ensure_ascii=False, indent=4)

            elif tep_json == 'ZombieStringsTranslate.json':
                muc: str = 'zombies'
                du_lieu: list = hop_nhat_ds(du_lieu_b.get(muc, []), du_lieu_a.get(muc, []), 'theZombieType')
                with open(tep_c, 'w', encoding='utf-8') as f:
                    json.dump({muc: du_lieu}, f, ensure_ascii=False, indent=4)

            else:
                du_lieu: dict = hop_nhat_dict(du_lieu_b, du_lieu_a)
                with open(tep_c, 'w', encoding='utf-8') as f:
                    json.dump(du_lieu, f, ensure_ascii=False, indent=4)

            print()

    if tep_moi:
        print('Các tệp mới:')
        for tep in tep_moi:
            print(f'- {tep}')

        print()


def so_sanh_strings() -> None:
    print('Mô đun Strings')
    phan_he: str = 'Strings'
    thu_muc_a = Path(dia_phuong, args.a, phan_he)
    if not thu_muc_a.is_dir():
        print(f'Thư mục {thu_muc_a} không tồn tại')
        sys.exit(1)

    thu_muc_b = Path(dia_phuong, args.b, phan_he)
    if not thu_muc_b.is_dir():
        print(f'Thư mục {thu_muc_b} không tồn tại')
        sys.exit(1)

    """Từ khóa có 2 dạng: str và dict"""

    # TODO


if __name__ == '__main__':
    tap_lenh = Path(__file__)
    thu_muc_goc = tap_lenh.parent
    parser = ArgumentParser(
        description='So sánh dữ liệu dịch thuật',
        epilog='Bản quyền © 2026 Vũ Đắc Hoàng Ân',
        formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('-v', '--version', action='version', version='So sánh Json 1.0.0')
    parser.add_argument('modun', help='Mô đun cần so sánh (Almanac hoặc Strings)')
    parser.add_argument('a', nargs='?', default='Vietnamese', help='Ngôn ngữ đích (mặc định: tiếng Việt)')
    parser.add_argument('b', nargs='?', default='English', help='Ngôn ngữ nguồn (mặc định: tiếng Anh)')
    args: Namespace = parser.parse_args()

    ds_phan_he: list = ['Almanac', 'Strings']
    if args.modun not in ds_phan_he:
        print('Mô đun không hợp lệ. Chỉ hỗ trợ Almanac hoặc Strings')
        sys.exit(1)

    tam = Path(thu_muc_goc, '../PvZ_Fusion_Translator/Localization')
    dia_phuong = tam.resolve()
    if not dia_phuong.is_dir():
        print(f'Thư mục {dia_phuong} không tồn tại')
        sys.exit(1)

    if args.modun == 'Almanac':
        so_sanh_almanac()
    elif args.modun == 'Strings':
        so_sanh_strings()

    print('Xong')
