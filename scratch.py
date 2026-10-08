from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.getOrCreate()
spark.sql("SELECT 1 AS ok").show()
spark.sql("SELECT * FROM silver_country_hs_code_trade_weight_summary LIMIT 5").show()