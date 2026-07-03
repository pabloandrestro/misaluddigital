-- =========================================================
-- schema
-- =========================================================

CREATE SCHEMA IF NOT EXISTS "public";

CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- =========================================================
-- enum types
-- no se crean blood_type ni user_role
-- porque eran usados por tablas administradas por django
-- =========================================================

CREATE TYPE "public"."center_type" AS ENUM (
    'hospital_publico',
    'cesfam',
    'clinica_privada',
    'farmacia',
    'urgencia',
    'other'
);

CREATE TYPE "public"."doc_type" AS ENUM (
    'exam',
    'prescription',
    'sick_leave',
    'report',
    'vaccine',
    'other'
);

CREATE TYPE "public"."priority" AS ENUM (
    'low',
    'medium',
    'high'
);


-- =========================================================
-- tables
-- users y medical_profiles quedan fuera
-- porque las administrara django
-- =========================================================

CREATE TABLE "public"."document_categories" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "name" varchar(100) NOT NULL,
    "slug" varchar(100) NOT NULL UNIQUE,
    "icon" varchar(100) NOT NULL DEFAULT '',

    PRIMARY KEY ("id")
);

CREATE TABLE "public"."health_centers" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "name" varchar NOT NULL,
    "center_type" "public"."center_type" NOT NULL,
    "address" varchar,
    "region" varchar,
    "comuna" varchar,
    "lat" real,
    "lng" real,
    "phone" varchar,
    "services" text[] NOT NULL DEFAULT '{}',

    PRIMARY KEY ("id")
);

CREATE TABLE "public"."documents" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "category_id" uuid,
    "title" varchar NOT NULL,
    "doc_type" "public"."doc_type" NOT NULL DEFAULT 'other',
    "file_key" varchar NOT NULL,
    "file_url" varchar,
    "mime_type" varchar,
    "file_size_bytes" int,
    "document_date" date,
    "issuing_institution" varchar,
    "issuing_professional" varchar,
    "specialty" varchar(255),
    "favorite" boolean NOT NULL DEFAULT FALSE,
    "bucket_name" varchar(150) NOT NULL,
    "extracted_text" text NOT NULL DEFAULT '',
    "ai_metadata" jsonb NOT NULL DEFAULT '{}'::jsonb,
    "created_at" timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" timestamptz,

    PRIMARY KEY ("id")
);

CREATE TABLE "public"."ai_recommendations" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "title" varchar NOT NULL,
    "body" text NOT NULL,
    "priority" "public"."priority" NOT NULL DEFAULT 'low',
    "is_read" boolean NOT NULL DEFAULT FALSE,
    "created_at" timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY ("id")
);

CREATE TABLE "public"."audit_logs" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid,
    "action" varchar(100) NOT NULL,
    "entity_type" varchar(50),
    "entity_id" uuid,
    "metadata" jsonb,
    "created_at" timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY ("id")
);

CREATE TABLE "public"."temporary_access_links" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "token" varchar(255) NOT NULL UNIQUE,
    "professional_name" varchar(150) NOT NULL,
    "professional_rut" varchar(12) NOT NULL,
    "document_ids" jsonb NOT NULL DEFAULT '[]'::jsonb,
    "expires_at" timestamptz NOT NULL,
    "accessed_at" timestamptz,
    "created_at" timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY ("id")
);

-- =========================================================
-- indexes
-- =========================================================

CREATE INDEX "health_centers_comuna_idx"
ON "public"."health_centers" ("comuna");

CREATE INDEX "health_centers_region_idx"
ON "public"."health_centers" ("region");

CREATE INDEX "documents_user_idx"
ON "public"."documents" ("user_id");

CREATE INDEX "documents_category_idx"
ON "public"."documents" ("category_id");

CREATE INDEX "documents_date_idx"
ON "public"."documents" ("document_date");

CREATE INDEX "documents_active_idx"
ON "public"."documents" ("user_id")
WHERE "deleted_at" IS NULL;

CREATE INDEX "ai_recommendations_user_idx"
ON "public"."ai_recommendations" ("user_id");

CREATE INDEX "audit_logs_action_idx"
ON "public"."audit_logs" ("action");

CREATE INDEX "audit_logs_date_idx"
ON "public"."audit_logs" ("created_at");

CREATE INDEX "audit_logs_user_idx"
ON "public"."audit_logs" ("user_id");

CREATE INDEX "temporary_access_links_expiry_idx"
ON "public"."temporary_access_links" ("expires_at");

CREATE INDEX "temporary_access_links_user_idx"
ON "public"."temporary_access_links" ("user_id");


-- =========================================================
-- foreign key constraints
-- users viene desde django
-- =========================================================

ALTER TABLE "public"."documents"
ADD CONSTRAINT "fk_documents_user_id_users_id"
FOREIGN KEY ("user_id")
REFERENCES "public"."users" ("id");

ALTER TABLE "public"."documents"
ADD CONSTRAINT "fk_documents_category_id_document_categories_id"
FOREIGN KEY ("category_id")
REFERENCES "public"."document_categories" ("id");

ALTER TABLE "public"."ai_recommendations"
ADD CONSTRAINT "fk_ai_recommendations_user_id_users_id"
FOREIGN KEY ("user_id")
REFERENCES "public"."users" ("id");

ALTER TABLE "public"."audit_logs"
ADD CONSTRAINT "fk_audit_logs_user_id_users_id"
FOREIGN KEY ("user_id")
REFERENCES "public"."users" ("id");

ALTER TABLE "public"."temporary_access_links"
ADD CONSTRAINT "fk_temporary_access_links_user_id_users_id"
FOREIGN KEY ("user_id")
REFERENCES "public"."users" ("id");

-- =========================================================
-- insert into para document_categories
-- con esta informacion se tendran los slugs
-- =========================================================

INSERT INTO
	document_categories (id, name, slug, icon)
VALUES
	(gen_random_uuid(), 'Recetas medicas', 'recetas-medicas', 'file-text'),
	(gen_random_uuid(), 'Examenes', 'examenes', 'flask-conical'),
	(gen_random_uuid(), 'Certificados', 'certificados', 'badge-check')
ON CONFLICT (slug) DO NOTHING;


-- =========================================================
-- supabase storage buckets (crear desde dashboard o CLI)
-- =========================================================
--
-- Bucket: profile-images
--   Público: false (privado)
--   Límite: 5242880 bytes (5 MB)
--   MIME permitidos: image/jpeg, image/png, image/webp
--   Políticas RLS: INSERT/UPDATE/SELECT solo si auth.uid() = user_id
--
-- Bucket: documents-recetas-medicas
--   Público: false (privado)
--   Límite: 10485760 bytes (10 MB)
--   MIME permitidos: application/pdf, image/jpeg, image/png, image/webp
--   Políticas RLS: SELECT/INSERT/UPDATE/DELETE solo si auth.uid() = user_id
--
-- Bucket: documents-examenes
--   Público: false (privado)
--   Límite: 10485760 bytes (10 MB)
--   MIME permitidos: application/pdf, image/jpeg, image/png, image/webp
--   Políticas RLS: SELECT/INSERT/UPDATE/DELETE solo si auth.uid() = user_id
--
-- Bucket: documents-certificados
--   Público: false (privado)
--   Límite: 10485760 bytes (10 MB)
--   MIME permitidos: application/pdf, image/jpeg, image/png, image/webp
--   Políticas RLS: SELECT/INSERT/UPDATE/DELETE solo si auth.uid() = user_id