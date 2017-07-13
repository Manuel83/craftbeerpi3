CREATE TABLE IF NOT EXISTS schema_info
(
    id INTEGER PRIMARY KEY NOT NULL,
    version INTEGER,
    filename VARCHAR(80),
    creation_data DEFAULT CURRENT_TIMESTAMP
);


INSERT OR IGNORE INTO config VALUES ('step_mashin', 'MashStep', 'step', 'Default MashIn Step type for import', NULL );
INSERT OR IGNORE INTO config VALUES ('step_mash', 'MashStep', 'step', 'Default Mash Step type for import', NULL);
INSERT OR IGNORE INTO config VALUES ('step_boil', 'BoilStep', 'step', 'Default Boil Step type for import', NULL);
INSERT OR IGNORE INTO config VALUES ('step_chil', 'ChilStep', 'step', 'Default Chil Step type for import', NULL);
INSERT OR IGNORE INTO config VALUES ('step_mash_kettle', 1, 'kettle', 'Default Mash Tun', NULL);
INSERT OR IGNORE INTO config VALUES ('step_boil_kettle', 1, 'kettle', 'Default Boil Tun ', NULL);



