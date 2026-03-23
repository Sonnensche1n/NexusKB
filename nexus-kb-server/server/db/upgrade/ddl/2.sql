CREATE TABLE IF NOT EXISTS "t_knb_dataset_index_error" (
  "dtset_id" text(32) NOT NULL,
  "idx_typ" text(10) NOT NULL,
  "err_inf" text,
  PRIMARY KEY ("dtset_id", "idx_typ")
);