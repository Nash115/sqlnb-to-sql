import os
import sqlite3
import sys
import time


def extract_notebook(filepath):
    if not os.path.isfile(filepath):
        print(f"Error : '{filepath}' not found.")
        sys.exit(1)
    try:
        conn = sqlite3.connect(filepath)
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM _sqlnotebook_items")
        items = cursor.fetchall()

        for item_id, name in items:
            safe_name = "".join(
                c for c in name if c.isalnum() or c in (" ", "_", "-")
            ).strip()
            out_filename = f"{safe_name}_{round(time.time())}.sql"

            query = """
                SELECT block_index, content, 'text' AS block_type
                FROM _sqlnotebook_page_text_blocks
                WHERE item_id = ?

                UNION ALL

                SELECT block_index, content, 'query' AS block_type
                FROM _sqlnotebook_page_query_blocks
                WHERE item_id = ?

                ORDER BY block_index ASC
            """

            cursor.execute(query, (item_id, item_id))
            blocks = cursor.fetchall()

            if not blocks:
                continue

            with open(out_filename, "w", encoding="utf-8") as f:
                for _, content, block_type in blocks:
                    if block_type == "text":
                        f.write(f"/*\n{content}\n*/\n\n")
                    else:
                        f.write(f"{content}\n\n")

            print(f"done : {out_filename} ({len(blocks)} blocks)")
        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite Error : {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} file.sqlnb")
        sys.exit(1)

    extract_notebook(sys.argv[1])
