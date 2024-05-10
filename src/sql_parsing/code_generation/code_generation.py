from io import TextIOWrapper
import datetime


class PropertyRecord:
    field_name: str
    typename: type

    def __init__(self, field_name: str, typename: type) -> None:
        self.field_name = field_name
        self.typename = typename

    def write(self, output_file, indentation_level: int, end_line: bool) -> None:
        output_file.write("\t" * indentation_level)
        output_file.write(f"{ self.field_name }: { ParseType.get_python_alias(self.typename) }")
        if (end_line):
            output_file.write("\n")


class Generator:
    output_file: TextIOWrapper
    def __init__(self, filename) -> None:
        self.filename = filename
        self.output_file = open(filename, "w")

    def __del__(self) -> None:
        self.output_file.close()


    def generate_class(self, class_name: str, records: list[PropertyRecord]) -> type:
        self.output_file.write(f"class {class_name}:\n")
        self.__generate_records(records)
        self.output_file.write("\n")
        self.__generate_constructor(records)
        self.output_file.flush()

        module = __import__(self.filename)
        return getattr(module, class_name)


    def __generate_records(self, records: list[PropertyRecord]):
        for record in records:
            record.write(self.output_file, 1, True)

    def __generate_constructor(self, records: list[PropertyRecord]):
        self.output_file.write("\tdef __init__ (self")
        for record in records:
            self.output_file.write(f", { record.field_name }")

        self.output_file.write("):\n")
        for record in records:
            if (record.typename == datetime.date):

                return
            self.output_file.write(
                f"\t\tself.{ record.field_name } = { ParseType.get_python_alias(record.typename) }({ record.field_name })\n")

