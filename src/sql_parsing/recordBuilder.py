"""
Syntax (for now):
    Columns must be comma seperated
    Columns must be fully qualified <table>.<column>
    Only one table after FROM
    Strict whitespace

    maybe not allow '*' at all

    if querry is invalid behaiviour is undefined

    postgres is case insensitive -> information lost

    DONE:
        AS keyword required

SQL structure
    SELECT
    FROM
    JOIN
    // WHERE + AND OR NOT
    GROUP BY
    // Having

"""

UNDEFINED_TABLE = "UNDEFINED_TABLE"

from .PeekingGenerator import PeekingGenerator
from .DatabaseDeamon import DatabaseDeamon
# import pyparsing
from pyparsing.core import Optional, Word, Suppress
from pyparsing.helpers import alphanums
import sqlparse
import psycopg2
from .code_generation.generator import PropertyRecord

from datetime import date

def translate_type(database_type: str) -> type:
    if (database_type == "character varying"):
        return str

    raise Exception(f"unknown type { database_type }")


class RecordBuilder:
    # ============ TOKEN GENERATION ===========
    @staticmethod # TODO move this to the PeekingGenerator
    def get_tokens(tokens):
        for token in tokens:
            if token.is_whitespace:
                continue
            # print(f"\t[yielding] { token.value }")
            yield token

    # ============== HELPERS ================
    @staticmethod
    def __parse_alias(value_and_alias: str) -> tuple[str, str]:
        """[TODO:description]

        Args:
            value_and_alias: [TODO:description]

        Returns:
            returns tuple of [ original_name, alias ]
        """
        alias_parsing_string = \
            Word(alphanums + ".").set_results_name("value")  \
            + Optional(
                Optional(Suppress(Word("AS")))  \
                + Word(alphanums).set_results_name("alias"))

        # this str cast is needed, not sure why
        parsed = alias_parsing_string.parseString(str(value_and_alias))
        value = parsed["value"]
        alias = parsed["alias"] if "alias" in parsed.keys() else value
        return str(value), str(alias)

    @staticmethod
    def __parse_table_alias(table_and_alias_value: str, table_alias_table) -> None:
        original_name, alias = RecordBuilder.__parse_alias(table_and_alias_value)
        table_alias_table[alias] = original_name

    @staticmethod
    def __resolve_aliases(column_values, table_aliases) -> list[ tuple[ str, str ] ]:
        # TODO this alows for multiple . in word maybe there is something like literal or constant
        parsing_expresion = \
            Word(alphanums).set_results_name("TableAlias") +  Suppress(Word(".")) + Word(alphanums).set_results_name("ColumnName")  \
            | Word(alphanums).set_results_name("ColumnName")

        # print(f"colum values aliased : { column_values }")
        result = []
        for column_value in column_values:
            parsed = parsing_expresion.parseString(str(column_value))

            table_alias = parsed["TableAlias"] if "TableAlias" in parsed.keys() else UNDEFINED_TABLE
            column_name = parsed["ColumnName"]

            result.append((table_aliases[table_alias], column_name))

        return result

    # ============= KEYWORD HELPERS ==========
    @staticmethod
    def __parse_columns_selected(token, values_aliases, values_list) -> None:
        # TODO handle "more than *" e.g. select *, count(*)
        if token.value == "*":
            values_list = [ "*" ]
            return
        for full_name in token.value.split(","):
            column_name, table_alias  = RecordBuilder.__parse_alias(full_name)

            # TODO is strip needed?
            values_list.append(column_name.strip())
            values_aliases[table_alias.strip()] = column_name.strip()


    # ============= MAIN PARSING
    @staticmethod
    def __get_tables_layout(connection, table_aliases: dict[ str, str ]):
        return {
            table_name : DatabaseDeamon.querry(connection, table_name)
            for table_name in table_aliases.values()
        }

    @staticmethod
    def __parse_inner(connection, querry: str):

        formated = sqlparse.format(querry.lower(), keyword_case="upper")
        parsed = sqlparse.parse(formated)
        statment = parsed[0]
        if (statment.get_type() != "SELECT"):
            raise Exception("Cannot typeprovide for non-select statment")
        tokens = PeekingGenerator(RecordBuilder.get_tokens(statment.tokens))

        column_values = []
        column_aliases = {}
        table_aliases = {}

        while True:
            try: # TODO better way to detect end of iteration
                token = next(tokens)
            except StopIteration:
                break

            if token.is_keyword:
                if token.value == "SELECT":
                    RecordBuilder.__parse_columns_selected(next(tokens), column_aliases, column_values)
                    continue

                if token.value == "FROM":
                    table_with_alias = next(tokens)
                    RecordBuilder.__parse_table_alias(table_with_alias, table_aliases)
                    continue

                if token.value == "JOIN":
                    what = next(tokens)
                    assert(next(tokens).value == "ON")
                    __join_condition = next(tokens)
                    RecordBuilder.__parse_table_alias(what, table_aliases)
                    continue

                if token.value == "WHERE": # WHERE and HAVING don't alter table structure
                    # skip everything until you find
                    # - GroupBy
                    # - orderby
                    # - -Sortby
                    # but safer way to do it is skip everything until we find keyword that is neither 'AND' nor 'OR'
                    while True:
                        try:
                            next_val = next(tokens)
                            if next_val.is_keyword and next_val.value not in ("AND", "OR"):
                                break
                        except StopIteration:
                            break

                    continue

                # TODO:
                # It seems if there is groupby only restrictions are
                # - don't use wildcart '*' after select
                # - Columns not mentioned in groupby go OOS
                # - certain agregation functions get enabled
                # if token.value == "GROUP BY": # TODO

                if token.value == "HAVING": # WHERE and HAVING don't alter table structure
                    continue


                print(f"UNIMPLEMENTED KEYWORD { token.value }")
                continue

            # TODO TOKEN PUNCTUIATION

            print(f"unimplemented token { token.value } : { token.ttype }")

        table_layouts = RecordBuilder.__get_tables_layout(connection, table_aliases)
        # ======= DEBUG
        # print("finished with")
        # print(column_values)
        # print(column_aliases)
        # print(table_aliases)
        # print(table_layouts)

        # ====== Define full column names
        return RecordBuilder.__resolve_aliases(column_values, table_aliases), table_layouts

    @staticmethod
    def parse(connection, querry: str) -> list[ PropertyRecord ]:
        print(f"Querry in: { querry }")
        columns, tables_layout = RecordBuilder.__parse_inner(connection, querry)

        result = []
        for col in columns:
            table_name, column_name = col;
            if table_name != UNDEFINED_TABLE:
                result.append(
                    PropertyRecord(column_name, translate_type(tables_layout[table_name][column_name])))
            else:
                for table_schema in tables_layout.values():
                    if column_name in table_schema.keys():
                        result.append(
                            PropertyRecord(column_name, translate_type(table_schema[column_name])))

                        break

        print(f"Result from parsing: { result }")
        return result

