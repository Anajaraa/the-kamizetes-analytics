#Análise exploratória dos dados (EDA) para entender as principais tendências e padrões nas vendas, focando especialmente na região Sul.

import pandas as pd

# =========================
# LOAD DATA
# =========================
fact = pd.read_parquet("data/processed/fact_sales.parquet")

print("\nShape:", fact.shape)

# =========================
# RECEITA TOTAL
# =========================
total_revenue = fact["Sales"].sum()
print("\nReceita Total:", round(total_revenue, 2))

# =========================
# RECEITA POR ANO/MÊS
# =========================
monthly_revenue = (
    fact.groupby("order_yyyymm")["Sales"]
    .sum()
    .sort_index()
)

print("\nReceita por mês:")
print(monthly_revenue.head())

# =========================
# RECEITA POR REGIÃO
# =========================
region_revenue = (
    fact.groupby("Region")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\nReceita por região:")
print(region_revenue)

# =========================
# FOCO SUL
# =========================
south_sales = fact[fact["market_focus"] == "Sul"]["Sales"].sum()
other_sales = fact[fact["market_focus"] == "Outros"]["Sales"].sum()

print("\nReceita Sul:", round(south_sales, 2))
print("Receita Outros:", round(other_sales, 2))

# =========================
# TOP PRODUTOS
# =========================
top_products = (
    fact.groupby("Product_Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\nTop 10 produtos:")
print(top_products)
