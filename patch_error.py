import re

with open("api/db.py", "r") as f:
    text = f.read()

new_except = """
    except Exception as e:
        import traceback
        with open("db_errors.log", "a") as ef:
            ef.write(f"Error saving verification to DB for {bank_id}: {e}\n{traceback.format_exc()}\n==========\n")
        print(f"Error saving verification to DB for {bank_id}: {e}")
"""

text = re.sub(
    r'    except Exception as e:[\s\S]*?print\(f"Error saving verification to DB for \{bank_id\}: \{e\}"\)',
    new_except.strip(),
    text
)

with open("api/db.py", "w") as f:
    f.write(text)

