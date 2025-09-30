import json
import re
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from app.service.upload.handlers.utils import StreamFileHandler


class SQLDialectConverter:
    """
    Handles conversion between different SQL dialects to SQLite for execution.
    """

    @staticmethod
    def detect_dialect(sql_script: str) -> str:
        """
        Detect the SQL dialect based on syntax patterns.
        """
        # Look for dialect-specific keywords and patterns
        if re.search(
            r"\bDELIMITER\b|\bBEGIN\s+TRANSACTION\b", sql_script, re.IGNORECASE
        ):
            return "mysql"
        elif re.search(
            r"\bPLPGSQL\b|\bRETURN\s+SETOF\b|\bCREATE\s+SEQUENCE\b",
            sql_script,
            re.IGNORECASE,
        ):
            return "postgresql"
        elif re.search(
            r"\bEXEC\b|\bGO\b|\bDECLARE\s+@\w+\b", sql_script, re.IGNORECASE
        ):
            return "sqlserver"
        elif re.search(
            r"\bBEGIN\s+EXECUTE\s+IMMEDIATE\b|\bPACKAGE\b|\bPL/SQL\b",
            sql_script,
            re.IGNORECASE,
        ):
            return "oracle"
        else:
            return "sqlite"

    @staticmethod
    def convert_to_sqlite(sql_script: str, dialect: str) -> str:
        """
        Convert SQL from a specific dialect to SQLite compatible syntax.
        """
        if dialect == "sqlite":
            return sql_script

        converted_script = sql_script

        # Remove dialect-specific transaction markers
        converted_script = re.sub(
            r"\bBEGIN\s+TRANSACTION\b|\bCOMMIT\b|\bROLLBACK\b",
            "",
            converted_script,
            flags=re.IGNORECASE,
        )

        if dialect == "mysql":
            converted_script = re.sub(
                r"AUTO_INCREMENT",
                "AUTOINCREMENT",
                converted_script,
                flags=re.IGNORECASE,
            )
            converted_script = re.sub(
                r"ENGINE\s*=\s*\w+", "", converted_script, flags=re.IGNORECASE
            )
            converted_script = re.sub(
                r"CHARSET\s*=\s*\w+", "", converted_script, flags=re.IGNORECASE
            )
            # Remove DELIMITER statements
            converted_script = re.sub(
                r"DELIMITER\s*;?\s*", "", converted_script, flags=re.IGNORECASE
            )

        elif dialect == "postgresql":
            converted_script = re.sub(
                r"SERIAL",
                "INTEGER PRIMARY KEY AUTOINCREMENT",
                converted_script,
                flags=re.IGNORECASE,
            )
            converted_script = re.sub(
                r"BYTEA", "BLOB", converted_script, flags=re.IGNORECASE
            )
            converted_script = re.sub(
                r"TEXT\[\]", "TEXT", converted_script, flags=re.IGNORECASE
            )

        elif dialect == "sqlserver":
            converted_script = re.sub(
                r"IDENTITY\(\d+,\d+\)",
                "AUTOINCREMENT",
                converted_script,
                flags=re.IGNORECASE,
            )
            converted_script = re.sub(
                r"NVARCHAR\((\w+)\)",
                r"VARCHAR(\1)",
                converted_script,
                flags=re.IGNORECASE,
            )
            converted_script = re.sub(
                r"\bGO\b", "", converted_script, flags=re.IGNORECASE
            )

        elif dialect == "oracle":
            converted_script = re.sub(
                r"NUMBER(\(\d+,\d+\))?", r"REAL", converted_script, flags=re.IGNORECASE
            )
            converted_script = re.sub(
                r"NUMBER(\(\d+\))?", r"INTEGER", converted_script, flags=re.IGNORECASE
            )
            converted_script = re.sub(
                r"VARCHAR2", "VARCHAR", converted_script, flags=re.IGNORECASE
            )

        # Extract only the CREATE TABLE and INSERT statements for basic compatibility
        create_statements = re.findall(
            r"CREATE\s+TABLE\s+[^;]+;", converted_script, re.IGNORECASE | re.DOTALL
        )
        insert_statements = re.findall(
            r"INSERT\s+INTO\s+[^;]+;", converted_script, re.IGNORECASE | re.DOTALL
        )

        # Combine the extracted statements
        sqlite_compatible = "\n".join(create_statements + insert_statements)

        # If we couldn't extract any valid statements, return the best effort conversion
        if not sqlite_compatible:
            return converted_script

        return sqlite_compatible

    @staticmethod
    def extract_schema_info(sql_script: str) -> List[Dict[str, Any]]:
        """
        Extract schema information from SQL CREATE statements.
        """
        schema_info = []

        # Find CREATE TABLE statements
        create_statements = re.findall(
            r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\`\"\[]{0,1}(\w+)[\`\"\]]{0,1}\s*\((.*?)\);",
            sql_script,
            re.IGNORECASE | re.DOTALL,
        )

        for table_name, columns_part in create_statements:
            # Clean table name
            table_name = re.sub(r"[\`\"\[\]]", "", table_name)

            # Extract column definitions
            columns = []
            for column_def in re.findall(
                r"[\`\"\[]{0,1}(\w+)[\`\"\]]{0,1}\s+([^,\)]+)", columns_part
            ):
                column_name = re.sub(r"[\`\"\[\]]", "", column_def[0])
                data_type = column_def[1].strip().split()[0].upper()
                columns.append({"name": column_name, "type": data_type})

            schema_info.append({"table": table_name, "columns": columns})

        return schema_info


class SQLParser:
    """
    Parser for extracting structured data from SQL files.
    """

    @staticmethod
    def parse_create_table(sql_script: str) -> List[Tuple[str, List[str]]]:
        """
        Extract table names and column definitions from CREATE TABLE statements.
        """
        tables = []

        # Find CREATE TABLE statements with their column definitions
        create_statements = re.findall(
            r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\`\"\[]{0,1}(\w+)[\`\"\]]{0,1}\s*\((.*?)\);",
            sql_script,
            re.IGNORECASE | re.DOTALL,
        )

        for table_name, columns_part in create_statements:
            # Clean table name
            table_name = re.sub(r"[\`\"\[\]]", "", table_name)

            # Extract column names
            column_names = []
            for column_match in re.finditer(
                r"[\`\"\[]{0,1}(\w+)[\`\"\]]{0,1}\s+([^,\)]+)", columns_part
            ):
                column_name = re.sub(r"[\`\"\[\]]", "", column_match.group(1))
                column_names.append(column_name)

            tables.append((table_name, column_names))

        return tables

    @staticmethod
    def parse_insert_statements(sql_script: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract data from INSERT statements.
        """
        table_data: Dict[str, List[Dict[str, Any]]] = {}

        # Find INSERT statements
        for match in re.finditer(
            r"INSERT\s+INTO\s+[\`\"\[]{0,1}(\w+)[\`\"\]]{0,1}\s*(?:\((.*?)\))?\s*VALUES\s*\((.*?)\);",
            sql_script,
            re.IGNORECASE | re.DOTALL,
        ):
            table_name = re.sub(r"[\`\"\[\]]", "", match.group(1))
            columns_str = match.group(2)
            values_str = match.group(3)

            # If columns aren't specified, we'll need to get them from CREATE TABLE
            columns = []
            if columns_str:
                columns = [
                    re.sub(r"[\`\"\[\]]", "", col.strip())
                    for col in columns_str.split(",")
                ]

            # Parse values
            # This is simplified and doesn't handle all SQL value formats
            values = SQLParser._parse_values(values_str)

            if table_name not in table_data:
                table_data[table_name] = []

            if columns:
                row_data = {
                    columns[i]: values[i] if i < len(values) else None
                    for i in range(len(columns))
                }
            else:
                # If no columns specified, we'll use indices
                row_data = {f"column_{i}": values[i] for i in range(len(values))}

            table_data[table_name].append(row_data)

        return table_data

    @staticmethod
    def _parse_values(values_str: str) -> List[Any]:
        """
        Parse the values part of an INSERT statement.
        Handle different quoting styles and properly remove quotes.
        """
        values: List[Any] = []
        # Split by commas but respect quoted strings
        # This is a simplistic approach to handle basic cases
        value_parts: List[str] = []
        in_quotes = False
        quote_char = None
        current_part = ""

        for char in values_str:
            if char in ["'", '"']:
                if not in_quotes:
                    # Starting a quoted section
                    in_quotes = True
                    quote_char = char
                    current_part += char
                elif char == quote_char:
                    # Ending a quoted section
                    in_quotes = False
                    quote_char = None
                    current_part += char
                else:
                    # A quote character inside a differently quoted string
                    current_part += char
            elif char == "," and not in_quotes:
                # End of a value
                value_parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char

        # Add the last part if there is one
        if current_part.strip():
            value_parts.append(current_part.strip())

        # Process each part
        for part in value_parts:
            # Remove quotes if present
            if (part.startswith("'") and part.endswith("'")) or (
                part.startswith('"') and part.endswith('"')
            ):
                # Remove the quotes
                value = part[1:-1]
            else:
                value = part

            # Try to convert to appropriate type
            if value.lower() == "null":
                values.append(None)
            elif value.isdigit():
                values.append(int(value))
            else:
                try:
                    float_val = float(value)
                    values.append(float_val)
                except ValueError:
                    values.append(value)  # Keep as string if not a number

        return values


class SQLStreamFileHandler(StreamFileHandler):
    """
    Handles SQL file streaming with support for multiple dialects.
    """

    def __init__(self, filename: str, file_type: str = "sql"):
        super().__init__(file_type=file_type, filename=filename)
        self.current_data: List[str] = []
        self.dialect: Optional[str] = None

    async def create_file(self, extension: str = "json") -> None:
        await super().create_file()
        await self.file_info.handle.write("[")

    async def write_data(self, data: list[str]) -> None:
        """Process SQL data chunk and store for later conversion"""
        for line in data:
            line = line.strip()
            if line:
                self.current_data.append(line)

    async def finalize(self) -> None:
        """Convert SQL to JSON and finalize the file"""
        sql_script = "\n".join(self.current_data)

        # Try the SQLite approach first
        sqlite_result = await self._process_with_sqlite(sql_script)

        # If SQLite processing fails or returns no data, try the regex-based parser
        if not sqlite_result:
            regex_result = self._process_with_regex_parser(sql_script)

            # Write regex-based parsing results
            for entry in regex_result:
                if self.file_info.count > 0:
                    await self.file_info.handle.write(",")
                # Write the JSON object to the file
                await self.file_info.handle.write(json.dumps(entry, ensure_ascii=False))
                self.file_info.count += 1

        # Close the JSON array
        await self.file_info.handle.write("]")
        await self.file_info.handle.close()

    async def _process_with_sqlite(self, sql_script: str) -> bool:
        """
        Process SQL using SQLite engine with dialect conversion.
        Returns True if processing was successful and data was written.
        """
        # Detect SQL dialect
        self.dialect = SQLDialectConverter.detect_dialect(sql_script)

        # Convert to SQLite compatible syntax
        sqlite_compatible = SQLDialectConverter.convert_to_sqlite(
            sql_script, self.dialect
        )

        # Create temporary SQLite database in memory
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        try:
            # Add metadata about original dialect
            dialect_entry = {
                "_meta": {
                    "original_dialect": self.dialect,
                    "processing_method": "sqlite_engine",
                }
            }

            await self.file_info.handle.write(
                json.dumps(dialect_entry, ensure_ascii=False)
            )

            self.file_info.count += 1

            # Execute the converted SQL
            cursor.executescript(sqlite_compatible)
            conn.commit()

            # Get all tables in the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            # Extract data from each table
            table_count = 0
            for table in tables:
                table_name = table[0]

                # Skip sqlite system tables
                if table_name.startswith("sqlite_"):
                    continue

                cursor.execute(f"SELECT * FROM {table_name}")
                columns = [description[0] for description in cursor.description]

                rows = cursor.fetchall()
                for row in rows:
                    entry = {
                        "_table": table_name,
                        **{columns[i]: row[i] for i in range(len(columns))},
                    }

                    if self.file_info.count > 0:
                        await self.file_info.handle.write(",")

                    # Write the JSON object to the file
                    await self.file_info.handle.write(
                        json.dumps(entry, ensure_ascii=False)
                    )
                    self.file_info.count += 1

                table_count += 1

            # Return success if we processed at least one table
            return table_count > 0

        except sqlite3.Error as e:
            # If SQLite processing fails, log the error but continue to try regex-based parsing
            error_entry = {
                "_meta": {
                    "error": f"SQLite processing error: {str(e)}",
                    "original_dialect": self.dialect,
                    "processing_method": "sqlite_engine_failed",
                }
            }

            if self.file_info.count > 0:
                await self.file_info.handle.write(",")

            # Write the error entry to the file
            await self.file_info.handle.write(
                json.dumps(error_entry, ensure_ascii=False)
            )

            self.file_info.count += 1

            # Close the database connection
            conn.close()
            return False

        finally:
            # Ensure the database connection is closed
            conn.close()

    def _process_with_regex_parser(self, sql_script: str) -> List[Dict[str, Any]]:
        """
        Process SQL using regex-based parsing as a fallback when SQLite engine fails.
        """
        result: List[Dict[str, Any]] = []

        # Add metadata
        result.append(
            {
                "_meta": {
                    "original_dialect": self.dialect
                    or SQLDialectConverter.detect_dialect(sql_script),
                    "processing_method": "regex_parser",
                }
            }
        )

        # Extract schema information
        schema_info = SQLDialectConverter.extract_schema_info(sql_script)
        if schema_info:
            result.append({"_schema": schema_info})

        # Parse table definitions
        tables = SQLParser.parse_create_table(sql_script)

        # Parse INSERT statements to extract data
        table_data = SQLParser.parse_insert_statements(sql_script)

        # Generate JSON records from parsed data
        for table_name, rows in table_data.items():
            for row in rows:
                entry = {"_table": table_name, **row}
                result.append(entry)

        # If no INSERT data was found but tables exist, add table structure info
        if not table_data and tables:
            for table_name, columns in tables:
                result.append({"_table_structure": table_name, "columns": columns})

        return result
