DROP TABLE IF EXISTS "t_doc_docmt_info";
CREATE TABLE "t_doc_docmt_info" (
  "doc_id" text(32) NOT NULL,
  "set_id" text(32),
  "doc_ttl" text(200),
  "doc_typ" text(10),
  "doc_sts" text(10),
  "doc_cntnt" text,
  "doc_pid" text(32),
  "doc_path" text(320),
  "crt_user" text(32),
  "crt_tm" text,
  "upd_tm" text,
  PRIMARY KEY ("doc_id")
);

DROP TABLE IF EXISTS "t_doc_docmt_version";
CREATE TABLE "t_doc_docmt_version" (
  "ver_id" text(32) NOT NULL,
  "doc_id" text(32),
  "set_id" text(32),
  "doc_ttl" text(200),
  "doc_typ" text(10),
  "doc_cntnt" text,
  "crt_user" text(32),
  "crt_tm" text,
  PRIMARY KEY ("ver_id")
);

DROP TABLE IF EXISTS "t_doc_docset_info";
CREATE TABLE "t_doc_docset_info" (
  "set_id" text(32) NOT NULL,
  "set_nm" text(200),
  "set_desc" text(2000),
  "set_icon" text(100),
  "auth_rang" text(10),
  "crt_user" text(32),
  "crt_tm" text,
  PRIMARY KEY ("set_id")
);

DROP TABLE IF EXISTS "t_knb_chat_info";
CREATE TABLE "t_knb_chat_info" (
  "chat_id" text(32) NOT NULL,
  "repos_id" text(32),
  "chat_ttl" text(200),
  "crt_user" text(32),
  "crt_tm" text,
  "last_tm" text,
  PRIMARY KEY ("chat_id")
);

DROP TABLE IF EXISTS "t_knb_chat_mesg";
CREATE TABLE "t_knb_chat_mesg" (
  "mesg_id" text(32) NOT NULL,
  "mesg_pid" text(32),
  "repos_id" text(32) NOT NULL,
  "chat_id" text(32),
  "mesg_cntnt" text,
  "mesg_typ" text(10),
  "crt_role" text(10),
  "crt_user" text(32),
  "crt_tm" text,
  PRIMARY KEY ("mesg_id")
);

DROP TABLE IF EXISTS "t_knb_dataset";
CREATE TABLE "t_knb_dataset" (
  "dtset_id" text(32) NOT NULL,
  "repos_id" text(32),
  "dtset_nm" text(200),
  "dtset_typ" text(10),
  "ctlg_id" text(32),
  "idx_sts" text(10),
  "prcs_sts" text(10),
  "qa_sts" text(10),
  "tplt_sts" text(10),
  "enb_sts" text(10),
  "file_nm" text(200),
  "file_typ" text(10),
  "file_path" text(500),
  "doc_id" text(32),
  "doc_ver_id" text(32),
  "crt_user" text(32),
  "crt_tm" text,
  PRIMARY KEY ("dtset_id")
);

DROP TABLE IF EXISTS "t_knb_dataset_chunk";
CREATE TABLE "t_knb_dataset_chunk" (
  "chk_id" text(32) NOT NULL,
  "dtset_id" text(32) NOT NULL,
  "repos_id" text(32),
  "chk_seq" integer,
  "chk_cntnt" text,
  "chk_asst" text,
  PRIMARY KEY ("chk_id")
);

DROP TABLE IF EXISTS "t_knb_dataset_ctlg";
CREATE TABLE "t_knb_dataset_ctlg" (
  "ctlg_id" text(32) NOT NULL,
  "ctlg_pid" text(32),
  "ctlg_path" text(320),
  "repos_id" text(32),
  "ctlg_nm" text(200),
  "ctlg_desc" text(2000),
  "ctlg_odr" integer,
  PRIMARY KEY ("ctlg_id")
);

DROP TABLE IF EXISTS "t_knb_dataset_index_error";
CREATE TABLE "t_knb_dataset_index_error" (
  "dtset_id" text(32) NOT NULL,
  "idx_typ" text(10) NOT NULL,
  "err_inf" text,
  PRIMARY KEY ("dtset_id", "idx_typ")
);

DROP TABLE IF EXISTS "t_knb_dataset_precis";
CREATE TABLE "t_knb_dataset_precis" (
  "prcs_id" text(32) NOT NULL,
  "dtset_id" text(32),
  "repos_id" text(32),
  "prcs_seq" integer,
  "prcs_cntnt" text,
  "prcs_src" text(10),
  PRIMARY KEY ("prcs_id")
);

DROP TABLE IF EXISTS "t_knb_dataset_triplet";
CREATE TABLE "t_knb_dataset_triplet" (
  "tplt_id" text(32) NOT NULL,
  "dtset_id" text(32),
  "repos_id" text(32),
  "tplt_seq" integer,
  "tplt_sbjct" text(1000),
  "tplt_prdct" text(1000),
  "tplt_objct" text(1000),
  "tplt_src" text(10),
  PRIMARY KEY ("tplt_id")
);

DROP TABLE IF EXISTS "t_knb_repos_info";
CREATE TABLE "t_knb_repos_info" (
  "repos_id" text(32) NOT NULL,
  "repos_nm" text(200),
  "repos_desc" text(2000),
  "repos_icon" text(100),
  "repos_typ" text(10),
  "vec_modl_id" text(32),
  "crt_user" text(32),
  "auth_rang" text(10),
  "crt_tm" text,
  PRIMARY KEY ("repos_id")
);

DROP TABLE IF EXISTS "t_knb_repos_quest";
CREATE TABLE "t_knb_repos_quest" (
  "qst_id" text(32) NOT NULL,
  "repos_id" text(32),
  "dtset_id" text(32),
  "qst_quest" text(2000),
  "qst_aswr" text,
  "qst_src" text(10),
  PRIMARY KEY ("qst_id")
);

DROP TABLE IF EXISTS "t_knb_srch_hist";
CREATE TABLE "t_knb_srch_hist" (
  "srch_id" text(32) NOT NULL,
  "repos_id" text(32),
  "srch_text" text(2000),
  "srch_typ" text(10),
  "srch_tm" text,
  "crt_user" text(32),
  PRIMARY KEY ("srch_id")
);

DROP TABLE IF EXISTS "t_sys_file_info";
CREATE TABLE "t_sys_file_info" (
  "file_id" text(32) NOT NULL,
  "file_nm" text(200),
  "file_path" text(500),
  "file_typ" text(10),
  "crt_user" text(32),
  "crt_tm" text,
  "file_size" integer,
  "md5_hex" text(32),
  "sha1_hex" text(40),
  "file_url" text(100),
  PRIMARY KEY ("file_id")
);

DROP TABLE IF EXISTS "t_sys_model_param";
CREATE TABLE "t_sys_model_param" (
  "prm_id" text(32) NOT NULL,
  "prvd_id" text(100) NOT NULL,
  "modl_id" text(32),
  "user_id" text(32) NOT NULL,
  "prm_cd" text(100) NOT NULL,
  "prm_val" text(2000),
  "val_ecrp" text(1),
  PRIMARY KEY ("prm_id")
);

DROP TABLE IF EXISTS "t_sys_model_prvd_info";
CREATE TABLE "t_sys_model_prvd_info" (
  "prvd_id" text(100) NOT NULL,
  "prvd_nm" text(200),
  "prvd_desc" text(2000),
  "prvd_icon" text(1000),
  "modl_typ" text(100),
  PRIMARY KEY ("prvd_id")
);

DROP TABLE IF EXISTS "t_sys_model_prvd_modl";
CREATE TABLE "t_sys_model_prvd_modl" (
  "prvd_id" text(100),
  "modl_nm" text(200),
  "modl_id" text(32) NOT NULL,
  "modl_typ" text(100),
  "modl_icon" text(1000),
  "user_id" text(32),
  "built_in" text(1),
  PRIMARY KEY ("modl_id")
);

DROP TABLE IF EXISTS "t_sys_model_prvd_param";
CREATE TABLE "t_sys_model_prvd_param" (
  "prvd_id" text(100) NOT NULL,
  "prm_cd" text(100) NOT NULL,
  "prm_nm" text(200),
  "prm_desc" text(2000),
  "dft_val" text(2000),
  "prm_lvl" text(10),
  "modl_typ" text(100),
  "prm_odr" integer,
  "not_null" text(1),
  "opt_vals" text(1000),
  "req_ecrp" text(1),
  PRIMARY KEY ("prm_cd", "prvd_id")
);

DROP TABLE IF EXISTS "t_sys_model_setting";
CREATE TABLE "t_sys_model_setting" (
  "user_id" text(32) NOT NULL,
  "prvd_id" text(100) NOT NULL,
  PRIMARY KEY ("user_id", "prvd_id")
);

DROP TABLE IF EXISTS "t_sys_schema_version";
CREATE TABLE "t_sys_schema_version" (
  "version" integer NOT NULL,
  PRIMARY KEY ("version")
);

DROP TABLE IF EXISTS "t_sys_setting_emrt";
CREATE TABLE "t_sys_setting_emrt" (
  "prm_id" text(32) NOT NULL,
  "val_cd" text(100) NOT NULL,
  "prm_cd" text(100),
  "user_id" text(32),
  "prm_val" text(2000),
  "val_odr" integer,
  PRIMARY KEY ("prm_id", "val_cd")
);

DROP TABLE IF EXISTS "t_sys_setting_param";
CREATE TABLE "t_sys_setting_param" (
  "prm_id" text(32) NOT NULL,
  "prm_cd" text(100),
  "prm_nm" text(200),
  "prm_val" text(2000),
  "whth_emrt" text(1),
  "user_id" text(32),
  "prm_desc" text(2000),
  PRIMARY KEY ("prm_id")
);

CREATE TABLE IF NOT EXISTS "t_knb_repos_setting" (
  "repos_id" text(32) NOT NULL,
  "max_ctx" integer,
  "max_hist" integer,
  "llm_tptur" decimal(10,2),
  "smlr_trval" decimal(10,2),
  "top_k" integer,
  PRIMARY KEY ("repos_id")
);

CREATE UNIQUE INDEX "T_SYS_MODEL_PARAM_UNIQUE_INDEX"
ON "t_sys_model_param" (
  "prvd_id" ASC,
  "modl_id" ASC,
  "user_id" ASC,
  "prm_cd" ASC
);
