# Business glossary entries.
# Each entry maps an ambiguous business term to its exact SQL/column meaning.
# These are indexed in schema_docs alongside real table metadata,
# so the retriever can surface them when a query uses these terms.

GLOSSARY_ENTRIES = [
    {
        "table_name": "__glossary__",
        "doc_text": (
            "Business term: revenue, total sales, income, earnings\n"
            "Definition: SUM of (unit_price * quantity) from invoice_items table, "
            "joined to invoices. Never use unit_price alone — always multiply by quantity.\n"
            "Relevant tables: invoice_items, invoices"
        ),
    },
    {
        "table_name": "__glossary__",
        "doc_text": (
            "Business term: top customers, best customers, highest spending customers\n"
            "Definition: customers ranked by SUM(invoices.total) descending. "
            "Join customers to invoices on customer_id.\n"
            "Relevant tables: customers, invoices"
        ),
    },
    {
        "table_name": "__glossary__",
        "doc_text": (
            "Business term: active customers, recent customers\n"
            "Definition: customers who have at least one invoice in the last 90 days. "
            "Use MAX(invoice_date) per customer and filter where that date >= NOW() - INTERVAL '90 days'.\n"
            "Relevant tables: customers, invoices"
        ),
    },
    {
        "table_name": "__glossary__",
        "doc_text": (
            "Business term: popular tracks, top tracks, best-selling songs\n"
            "Definition: tracks ranked by COUNT of times they appear in invoice_items. "
            "Join tracks → invoice_items on track_id.\n"
            "Relevant tables: tracks, invoice_items"
        ),
    },
    {
        "table_name": "__glossary__",
        "doc_text": (
            "Business term: sales trend, monthly sales, quarterly sales, yearly sales\n"
            "Definition: SUM(total) from invoices grouped by DATE_TRUNC('month', invoice_date) "
            "or DATE_TRUNC('year', invoice_date). Always alias the date column clearly.\n"
            "Relevant tables: invoices"
        ),
    },
    {
        "table_name": "__glossary__",
        "doc_text": (
            "Business term: average order value, AOV, average transaction\n"
            "Definition: AVG(total) from invoices table.\n"
            "Relevant tables: invoices"
        ),
    },
    {
        "table_name": "__glossary__",
        "doc_text": (
            "Business term: catalog size, number of tracks, library size\n"
            "Definition: COUNT(*) from tracks table. "
            "Can be filtered by genre (join tracks → genres on genre_id) "
            "or by album (join tracks → albums on album_id).\n"
            "Relevant tables: tracks, genres, albums"
        ),
    },
    {
        "table_name": "__glossary__",
        "doc_text": (
            "Business term: employee performance, sales rep performance\n"
            "Definition: total revenue attributed to each employee by joining "
            "customers.support_rep_id → employees.employee_id → invoices.customer_id.\n"
            "Relevant tables: employees, customers, invoices"
        ),
    },
]
