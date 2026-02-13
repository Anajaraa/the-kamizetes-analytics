import pandas as pd
import os

# Caminho do dataset
path = "data/raw/train.csv"

# Ler arquivo
df = pd.read_csv(path)

print("Shape:", df.shape)
print("\nColunas:")
print(df.columns)

print("\nPrimeiras linhas:")
print(df.head())

print("\nValores nulos:")
print(df.isna().sum().sort_values(ascending=False).head(10))

# ======================
# LIMPEZA
# ======================

# 1) Padronizar nomes de colunas
df.columns = [c.strip().replace(" ", "_").replace("-", "_") for c in df.columns]

# 2) Converter datas
df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
df["Ship_Date"]  = pd.to_datetime(df["Ship_Date"], errors="coerce")

# 3) Postal Code como texto
if "Postal_Code" in df.columns:
    df["Postal_Code"] = df["Postal_Code"].astype("string")

# 4) Remover duplicatas
if "Row_ID" in df.columns:
    df = df.drop_duplicates(subset=["Row_ID"], keep="first")

# 5) Filtrar registros essenciais
df = df.dropna(subset=["Order_ID", "Order_Date", "Ship_Date", "Sales"])

# 6) Garantir Sales válido
df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
df = df[df["Sales"] > 0]

print("\nApós limpeza:", df.shape)

# Lead time (dias)
df["ship_lead_days"] = (df["Ship_Date"] - df["Order_Date"]).dt.days

# Quebra de datas
df["order_year"] = df["Order_Date"].dt.year
df["order_month"] = df["Order_Date"].dt.month
df["order_yyyymm"] = df["Order_Date"].dt.to_period("M").astype(str)

df["weekday"] = df["Order_Date"].dt.weekday
df["weekday_name"] = df["Order_Date"].dt.day_name()
df["is_weekend"] = df["weekday"].isin([5, 6]).astype(int)

# Proxy "Sul do Brasil" (usando Region == South como recorte de mercado)
# (isso é só um recorte analítico; em empresa real seria PR/SC/RS)
if "Region" in df.columns:
    df["market_focus"] = df["Region"].apply(lambda x: "Sul" if str(x).strip().lower() == "south" else "Outros")
else:
    df["market_focus"] = "Outros"

print(df[["ship_lead_days","order_yyyymm","market_focus"]].head())


def make_collection(row):
    name = str(row.get("Product_Name", "")).lower()
    sub  = str(row.get("Sub_Category", "")).lower()
    cat  = str(row.get("Category", "")).lower()

    text = f"{cat} {sub} {name}"

    # regras simples (ajuste depois)
    if any(k in text for k in ["winter", "warm", "jacket", "coat", "sweat", "hood", "moletom"]):
        return "Winter Drop"
    if any(k in text for k in ["sport", "fit", "ath", "run", "gym"]):
        return "Sport"
    if any(k in text for k in ["geek", "game", "tech", "nerd"]):
        return "Geek"
    if any(k in text for k in ["minimal", "simple", "basic", "clean"]):
        return "Minimal"
    if any(k in text for k in ["street", "urban", "skate"]):
        return "Street"
    return "Core"

df["collection"] = df.apply(make_collection, axis=1)
df["collection"].value_counts()



# ==========================
# EXPORTAÇÃO MODELO ESTRELA
# ==========================

out_dir = "data/processed"
os.makedirs(out_dir, exist_ok=True)

# FACT COMPLETA
fact_sales = df.copy()
fact_sales.to_parquet(f"{out_dir}/fact_sales.parquet", index=False)

# DIM DATE
dim_date = (
    df[["Order_Date", "order_year", "order_month", "order_yyyymm", "weekday", "weekday_name", "is_weekend"]]
    .drop_duplicates()
    .rename(columns={"Order_Date": "date"})
)

dim_date.to_parquet(f"{out_dir}/dim_date.parquet", index=False)

# DIM CUSTOMER
dim_customer = (
    df[["Customer_ID", "Customer_Name", "Segment"]]
    .drop_duplicates()
)

dim_customer.to_parquet(f"{out_dir}/dim_customer.parquet", index=False)

# DIM PRODUCT
dim_product = (
    df[["Product_ID", "Category", "Sub_Category", "Product_Name", "collection"]]
    .drop_duplicates()
)

dim_product.to_parquet(f"{out_dir}/dim_product.parquet", index=False)

# DIM GEO
dim_geo = (
    df[["City", "State", "Region", "Country", "market_focus"]]
    .drop_duplicates()
)

dim_geo.to_parquet(f"{out_dir}/dim_geo.parquet", index=False)

print("Modelo estrela exportado corretamente.")

# DIM PRODUCT CORRETA
dim_product = (
    df[["Product_ID", "Product_Name", "Category", "Sub_Category", "collection"]]
    .drop_duplicates(subset=["Product_ID"])
)
dim_product.to_parquet("data/processed/dim_product.parquet", index=False)
