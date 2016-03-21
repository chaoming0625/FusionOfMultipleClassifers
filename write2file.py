import xlwt


class Write2File:
    def __init__(self):
        pass

    @staticmethod
    def append(filepath, content):
        if filepath is not None:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(content)

    @staticmethod
    def write(filepath, content):
        if filepath is not None:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

    @staticmethod
    def write_xls(filepath, contents):
        if isinstance(contents, list) and isinstance(contents[0], tuple):
            wb = xlwt.Workbook()
            ws = wb.add_sheet("Sheet 1")

            for i, (head, content) in enumerate(contents):
                ws.write(0, i, head)
                ws.write(1, i, content)

            wb.save(filepath)
