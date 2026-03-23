CREATE TABLE IF NOT EXISTS "t_knb_repos_setting" (
  "repos_id" text(32) NOT NULL,
  "max_ctx" integer,
  "max_hist" integer,
  "llm_tptur" decimal(10,2),
  "smlr_trval" decimal(10,2),
  "top_k" integer,
  PRIMARY KEY ("repos_id")
);