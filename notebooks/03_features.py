import pandas as pd

fact = pd.read_parquet("data/processed/fact_sales.parquet")

# =========================
# FEATURE 1: FLAG DE ENTREGA RÁPIDA
# =========================
fact["fast_delivery"] = fact["ship_lead_days"] <= 3

# =========================
# FEATURE 2: TICKET MÉDIO POR PEDIDO
# =========================
ticket = (
    fact.groupby("Order_ID")["Sales"]
    .sum()
    .reset_index()
)

ticket.rename(columns={"Sales": "ticket_value"}, inplace=True)

fact = fact.merge(ticket, on="Order_ID", how="left")

# =========================
# FEATURE 3: CLIENTE ALTO VALOR
# =========================
customer_value = (
    fact.groupby("Customer_ID")["Sales"]
    .sum()
    .reset_index()
)

threshold = customer_value["Sales"].quantile(0.75)

high_value_ids = customer_value[
    customer_value["Sales"] >= threshold
]["Customer_ID"]

fact["high_value_customer"] = fact["Customer_ID"].isin(high_value_ids)

# =========================
# SALVAR NOVA FACT
# =========================
fact.to_parquet("data/processed/fact_sales_enriched.parquet", index=False)

print("Feature engineering finalizada.")
