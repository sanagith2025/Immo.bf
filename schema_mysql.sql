-- ============================================================
-- IMMO-BF — Script SQL de création de la base de données
-- SGBD : MySQL 8+ / MariaDB 10.6+
-- Encodage : UTF-8
-- ============================================================

CREATE DATABASE IF NOT EXISTS immobf CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE immobf;

-- ── Utilisateurs ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS immobilier_utilisateur (
    id               BIGINT AUTO_INCREMENT PRIMARY KEY,
    email            VARCHAR(254) NOT NULL UNIQUE,
    password         VARCHAR(128) NOT NULL,
    nom              VARCHAR(100) NOT NULL,
    prenom           VARCHAR(100) NOT NULL,
    telephone        VARCHAR(20)  DEFAULT '',
    role             VARCHAR(20)  NOT NULL DEFAULT 'client'
                       CHECK (role IN ('visiteur','client','bailleur','agent','manager')),
    is_active        TINYINT(1)  NOT NULL DEFAULT 1,
    is_staff         TINYINT(1)  NOT NULL DEFAULT 0,
    is_superuser     TINYINT(1)  NOT NULL DEFAULT 0,
    date_inscription DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login       DATETIME    NULL,
    agent_affecte_id BIGINT      NULL,
    CONSTRAINT fk_agent_affecte FOREIGN KEY (agent_affecte_id)
        REFERENCES immobilier_utilisateur(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── Propriétés ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS immobilier_propriete (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    bailleur_id         BIGINT       NOT NULL,
    agent_validateur_id BIGINT       NULL,
    titre               VARCHAR(200) NOT NULL,
    type_bien           VARCHAR(20)  NOT NULL
                          CHECK (type_bien IN ('terrain','batiment','appartement','villa','commerce')),
    usage               VARCHAR(20)  NOT NULL
                          CHECK (usage IN ('residence','bureau','commerce','agriculture')),
    option              VARCHAR(10)  NOT NULL CHECK (option IN ('location','vente')),
    zone_geographique   VARCHAR(200) NOT NULL,
    superficie          DECIMAL(10,2) NOT NULL,
    prix                DECIMAL(15,0) NOT NULL,
    description         LONGTEXT     NOT NULL,
    statut              VARCHAR(20)  NOT NULL DEFAULT 'en_attente'
                          CHECK (statut IN ('en_attente','publiee','retiree','refusee')),
    est_agence          TINYINT(1)  NOT NULL DEFAULT 0,
    date_creation       DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_modification   DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_bailleur    FOREIGN KEY (bailleur_id)         REFERENCES immobilier_utilisateur(id) ON DELETE CASCADE,
    CONSTRAINT fk_validateur  FOREIGN KEY (agent_validateur_id) REFERENCES immobilier_utilisateur(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── Photos ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS immobilier_photopropriete (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    propriete_id BIGINT       NOT NULL,
    image       VARCHAR(200) NOT NULL,
    legende     VARCHAR(200) DEFAULT '',
    date_ajout  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_photo_propriete FOREIGN KEY (propriete_id)
        REFERENCES immobilier_propriete(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── Favoris ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS immobilier_favori (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    client_id   BIGINT NOT NULL,
    propriete_id BIGINT NOT NULL,
    date_ajout  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_favori (client_id, propriete_id),
    CONSTRAINT fk_fav_client   FOREIGN KEY (client_id)    REFERENCES immobilier_utilisateur(id) ON DELETE CASCADE,
    CONSTRAINT fk_fav_propriete FOREIGN KEY (propriete_id) REFERENCES immobilier_propriete(id)  ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── Demandes de visite ────────────────────────────────────
CREATE TABLE IF NOT EXISTS immobilier_demandevisite (
    id                 BIGINT AUTO_INCREMENT PRIMARY KEY,
    client_id          BIGINT      NOT NULL,
    propriete_id       BIGINT      NOT NULL,
    agent_id           BIGINT      NULL,
    message            LONGTEXT    DEFAULT '',
    date_souhaitee     DATE        NULL,
    statut             VARCHAR(20) NOT NULL DEFAULT 'en_attente'
                         CHECK (statut IN ('en_attente','validee','refusee')),
    date_demande       DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_traitement    DATETIME    NULL,
    commentaire_agent  LONGTEXT    DEFAULT '',
    CONSTRAINT fk_vis_client    FOREIGN KEY (client_id)    REFERENCES immobilier_utilisateur(id) ON DELETE CASCADE,
    CONSTRAINT fk_vis_propriete FOREIGN KEY (propriete_id) REFERENCES immobilier_propriete(id)  ON DELETE CASCADE,
    CONSTRAINT fk_vis_agent     FOREIGN KEY (agent_id)     REFERENCES immobilier_utilisateur(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── Données initiales : compte Manager ───────────────────
-- Mot de passe : Admin@2026  (haché bcrypt ci-dessous — à regénérer en production)
INSERT INTO immobilier_utilisateur
    (email, password, nom, prenom, role, is_active, is_staff, is_superuser)
VALUES (
    'manager@immobf.bf',
    'pbkdf2_sha256$870000$REMPLACEZ_PAR_HASH_GENERE$',
    'Administrateur', 'Principal', 'manager', 1, 1, 1
);

-- ============================================================
-- NOTE : Utiliser la commande Django pour créer le superuser :
--   python manage.py createsuperuser
-- ============================================================
