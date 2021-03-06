-- SGAS PostgreSQL functions

CREATE OR REPLACE FUNCTION urcreate (
    in_record_id               varchar,
    in_create_time             timestamp,
    in_global_job_id           varchar,
    in_local_job_id            varchar,
    in_local_user              varchar,
    in_global_user_name        varchar,
    in_vo_type                 varchar,
    in_vo_issuer               varchar,
    in_vo_name                 varchar,
    in_vo_attributes           varchar[][],
    in_machine_name            varchar,
    in_job_name                varchar,
    in_charge                  integer,
    in_status                  varchar,
    in_queue                   varchar,
    in_host                    varchar,
    in_node_count              integer,
    in_processors              integer,
    in_project_name            varchar,
    in_submit_host             varchar,
    in_start_time              timestamp,
    in_end_time                timestamp,
    in_submit_time             timestamp,
    in_cpu_duration            bigint,
    in_wall_duration           integer,
    in_user_time               integer,
    in_kernel_time             integer,
    in_major_page_faults       integer,
    in_runtime_environments    varchar[],
    in_exit_code               integer,
    in_downloads               varchar[],
    in_uploads                 varchar[],
    in_insert_host             varchar,
    in_insert_identity         varchar,
    in_insert_time             timestamp,
    in_memory                  sgas_memory[]
)
RETURNS varchar[] AS $recordid_rowid$

DECLARE
    local_user_fid          integer;
    globalusername_id       integer;
    voinformation_id        integer;
    machinename_id          integer;
    status_fid              integer;
    queue_fid               integer;
    host_fid                integer;
    project_name_fid        integer;
    submit_host_fid         integer;
    inserthost_id           integer;
    insertidentity_id       integer;
    runtime_environment_id  integer;
    jobtransferurl_id       integer;

    ur_id                   integer;
    ur_global_job_id        varchar;
    ur_machine_name_id      integer;
    ur_insert_time          date;

    result                  varchar[];
BEGIN
    -- first check that we do not have the record already
    SELECT usagedata.id, global_job_id, machine_name_id, insert_time::date
           INTO ur_id, ur_global_job_id, ur_machine_name_id, ur_insert_time
           FROM usagedata
           WHERE record_id = in_record_id;
    IF FOUND THEN
        -- this will decide if a record should replace another:
        -- if the global_job_id of the new record is similar to the global_job_id record
        -- it is considered identical. Furthermore if the global_job_id and the record_id
        -- of the incoming record are identical, the record is considered to have minimal
        -- information, and will not replace the existing record
        --
        -- this means that if the incoming record has global_job_id different from the existing
        -- record (they have the same record_id) and its global_job_id is different from the
        -- record_id, the new record will replace the existing record (the ELSE block)
        IF in_global_job_id = ur_global_job_id OR in_global_job_id = in_record_id THEN
            result[0] = in_record_id;
            result[1] = ur_id;
            RETURN result;
        ELSE
            -- delete record, mark update, and continue as normal
            -- technically we should delete job transfers and runtime environments first
            -- however records coming from the LRMS does not contain these, so if an error
            -- occurs here it usally due to an ARC/Grid bug.
            DELETE FROM usagedata WHERE record_id = in_record_id;
            PERFORM * FROM uraggregated_update WHERE insert_time = ur_insert_time::date AND machine_name_id = ur_machine_name_id;
            IF NOT FOUND THEN
                INSERT INTO uraggregated_update (insert_time, machine_name_id) VALUES (ur_insert_time, ur_machine_name_id);
            END IF;
        END IF;
    END IF;

    -- local user name
    IF in_local_user IS NULL THEN
        local_user_fid = NULL;
    ELSE
        SELECT INTO local_user_fid id FROM localuser WHERE local_user = in_local_user;
        IF NOT FOUND THEN
            INSERT INTO localuser (local_user) VALUES (in_local_user) RETURNING id INTO local_user_fid;
        END IF;
    END IF;

    -- global user name
    IF in_global_user_name IS NULL THEN
        globalusername_id = NULL;
    ELSE
        SELECT INTO globalusername_id id
               FROM globalusername
               WHERE global_user_name = in_global_user_name;
        IF NOT FOUND THEN
            INSERT INTO globalusername (global_user_name)
                VALUES (in_global_user_name) RETURNING id INTO globalusername_id;
        END IF;
    END IF;

    -- vo information
    IF in_vo_name is NULL THEN
        voinformation_id = NULL;
    ELSE
        SELECT INTO voinformation_id id
               FROM voinformation
               WHERE vo_type        IS NOT DISTINCT FROM in_vo_type AND
                     vo_issuer      IS NOT DISTINCT FROM in_vo_issuer AND
                     vo_name        IS NOT DISTINCT FROM in_vo_name AND
                     vo_attributes  IS NOT DISTINCT FROM in_vo_attributes;
        IF NOT FOUND THEN
            INSERT INTO voinformation (vo_type, vo_issuer, vo_name, vo_attributes)
                   VALUES (in_vo_type, in_vo_issuer, in_vo_name, in_vo_attributes) RETURNING id INTO voinformation_id;
        END IF;
    END IF;

    -- machine name
    IF in_machine_name IS NULL THEN
        machinename_id = NULL;
    ELSE
        SELECT INTO machinename_id id
               FROM machinename
               WHERE machine_name = in_machine_name;
        IF NOT FOUND THEN
            INSERT INTO machinename (machine_name) VALUES (in_machine_name) RETURNING id INTO machinename_id;
        END IF;
    END IF;

    -- status
    IF in_status IS NULL THEN
        status_fid = NULL;
    ELSE
        SELECT INTO status_fid id FROM jobstatus WHERE status = in_status;
        IF NOT FOUND THEN
            INSERT INTO jobstatus (status) VALUES (in_status) RETURNING id INTO status_fid;
        END IF;
    END IF;

    -- queue
    IF in_queue IS NULL THEN
        queue_fid = NULL;
    ELSE
        SELECT INTO queue_fid id FROM jobqueue WHERE queue = in_queue;
        IF NOT FOUND THEN
            INSERT INTO jobqueue (queue) VALUES (in_queue) RETURNING id INTO queue_fid;
        END IF;
    END IF;

    -- host
    IF in_host IS NULL THEN
        host_fid = NULL;
    ELSE
        SELECT INTO host_fid id FROM host WHERE host = in_host;
        IF NOT FOUND THEN
            INSERT INTO host (host) VALUES (in_host) RETURNING id INTO host_fid;
        END IF;
    END IF;

    -- project name
    IF in_project_name IS NULL THEN
        project_name_fid = NULL;
    ELSE
        SELECT INTO project_name_fid id FROM projectname WHERE project_name = in_project_name;
        IF NOT FOUND THEN
            INSERT INTO projectname (project_name) VALUES (in_project_name) RETURNING id INTO project_name_fid;
        END IF;
    END IF;

    -- submit host
    IF in_submit_host IS NULL THEN
        submit_host_fid = NULL;
    ELSE
        SELECT INTO submit_host_fid id FROM submithost WHERE submit_host = in_submit_host;
        IF NOT FOUND THEN
            INSERT INTO submithost (submit_host) VALUES (in_submit_host) RETURNING id INTO submit_host_fid;
        END IF;
    END IF;

    -- insert host
    IF in_insert_host IS NULL THEN
        inserthost_id = NULL;
    ELSE
        SELECT INTO inserthost_id id
               FROM inserthost
               WHERE insert_host = in_insert_host;
        IF NOT FOUND THEN
            INSERT INTO inserthost (insert_host) VALUES (in_insert_host) RETURNING id INTO inserthost_id;
        END IF;
    END IF;

    -- insert identity
    IF in_insert_identity IS NULL THEN
        insertidentity_id = NULL;
    ELSE
        SELECT INTO insertidentity_id id
               FROM insertidentity
               WHERE insert_identity = in_insert_identity;
        IF NOT FOUND THEN
            INSERT INTO insertidentity (insert_identity) VALUES (in_insert_identity) RETURNING id INTO insertidentity_id;
        END IF;
    END IF;

    INSERT INTO usagedata (
                        record_id,
                        create_time,
                        global_user_name_id,
                        vo_information_id,
                        machine_name_id,
                        global_job_id,
                        local_job_id,
                        local_user_id,
                        job_name,
                        charge,
                        status_id,
                        queue_id,
                        host_id,
                        node_count,
                        processors,
                        project_name_id,
                        submit_host_id,
                        start_time,
                        end_time,
                        submit_time,
                        cpu_duration,
                        wall_duration,
                        user_time,
                        kernel_time,
                        major_page_faults,
                        exit_code,
                        insert_host_id,
                        insert_identity_id,
                        insert_time,
			memory
                    )
            VALUES (
                        in_record_id,
                        in_create_time,
                        globalusername_id,
                        voinformation_id,
                        machinename_id,
                        in_global_job_id,
                        in_local_job_id,
                        local_user_fid,
                        in_job_name,
                        in_charge,
                        status_fid,
                        queue_fid,
                        host_fid,
                        in_node_count::smallint,
                        in_processors,
                        project_name_fid,
                        submit_host_fid,
                        in_start_time,
                        in_end_time,
                        in_submit_time,
                        in_cpu_duration,
                        in_wall_duration,
                        in_user_time,
                        in_kernel_time,
                        in_major_page_faults,
                        in_exit_code::smallint,
                        inserthost_id,
                        insertidentity_id,
                        in_insert_time,
			in_memory
                    )
            RETURNING id into ur_id;

    -- runtime environments
    IF in_runtime_environments IS NOT NULL THEN
        FOR i IN array_lower(in_runtime_environments, 1) .. array_upper(in_runtime_environments, 1) LOOP
            -- check if re exists, isert if it does not
            SELECT INTO runtime_environment_id id FROM runtimeenvironment WHERE runtime_environment = in_runtime_environments[i];
            IF NOT FOUND THEN
                INSERT INTO runtimeenvironment (runtime_environment) VALUES (in_runtime_environments[i]) RETURNING id INTO runtime_environment_id;
            END IF;
            -- insert record ur usage, perform duplicate check first though
            PERFORM * FROM runtimeenvironment_usagedata WHERE usagedata_id = ur_id AND runtime_environment_id = runtimeenvironments_id;
            IF NOT FOUND THEN
                INSERT INTO runtimeenvironment_usagedata (usagedata_id, runtimeenvironments_id) VALUES (ur_id, runtime_environment_id);
            END IF;
        END LOOP;
    END IF;

    -- create rows for file transfers
    IF in_downloads IS NOT NULL THEN
        FOR i IN array_lower(in_downloads, 1) .. array_upper(in_downloads, 1) LOOP
            -- check if url exists, insert if it does not
            SELECT INTO jobtransferurl_id id FROM jobtransferurl WHERE url = in_downloads[i][1];
            IF NOT FOUND THEN
                INSERT INTO jobtransferurl (url) VALUES (in_downloads[i][1]) RETURNING id INTO jobtransferurl_id;
            END IF;
            -- insert download
            INSERT INTO jobtransferdata (usage_data_id, job_transfer_url_id, transfer_type,
                                         size, start_time, end_time, bypass_cache, retrieved_from_cache)
                   VALUES (ur_id, jobtransferurl_id, 'download',
                           in_downloads[i][2]::bigint, in_downloads[i][3]::timestamp, in_downloads[i][4]::timestamp,
                           in_downloads[i][5]::boolean, in_downloads[i][6]::boolean);
        END LOOP;
    END IF;

    IF in_uploads IS NOT NULL THEN
        FOR i IN array_lower(in_uploads, 1) .. array_upper(in_uploads, 1) LOOP
            -- check if url exists, insert if it does not
            SELECT INTO jobtransferurl_id id FROM jobtransferurl WHERE url = in_uploads[i][1];
            IF NOT FOUND THEN
                INSERT INTO jobtransferurl (url) VALUES (in_uploads[i][1]) RETURNING id INTO jobtransferurl_id;
            END IF;
            -- insert upload
            INSERT INTO jobtransferdata (usage_data_id, job_transfer_url_id, transfer_type, size, start_time, end_time)
                   VALUES (ur_id, jobtransferurl_id, 'upload',
                           in_uploads[i][2]::bigint, in_uploads[i][3]::timestamp, in_uploads[i][4]::timestamp);
        END LOOP;
    END IF;

    -- finally we update the table describing what aggregated information should be updated
    PERFORM * FROM uraggregated_update WHERE insert_time = in_insert_time::date AND machine_name_id = machinename_id;
    IF NOT FOUND THEN
        INSERT INTO uraggregated_update (insert_time, machine_name_id) VALUES (in_insert_time::date, machinename_id);
    END IF;

    result[0] = in_record_id;
    result[1] = ur_id;
    RETURN result;

END;
$recordid_rowid$
LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION update_uraggregate ( )
RETURNS varchar[] AS $insertdate_machinename$

DECLARE
    q_insert_date       date;
    q_machine_name_id   integer;
    result              varchar[];
BEGIN
    -- the transaction isolation level for this function should be set to serializable
    -- unfortunately it is not possible to set in the function as a function always
    -- start a transaction, at which time it is to late to set it
    -- therefore we trust the caller of the function to set it for us

    -- get data for what to update
    SELECT insert_time, machine_name_id INTO q_insert_date, q_machine_name_id
        FROM uraggregated_update ORDER BY insert_time LIMIT 1;
    IF NOT FOUND THEN
        -- nothing to update
        RETURN result;
    END IF;

    -- delete aggregation update row
    DELETE FROM uraggregated_update WHERE insert_time = q_insert_date AND machine_name_id = q_machine_name_id;
    -- delete existing aggregated rows that will be updated
    DELETE FROM uraggregated_data WHERE insert_time = q_insert_date AND machine_name_id = q_machine_name_id;

    INSERT INTO uraggregated_data
        (execution_time, insert_time, machine_name_id, queue_id,
         global_user_name_id, local_user_id, vo_information_id, project_name_id,
         runtime_environments_id, status_id, insert_host_id, n_jobs, cputime, walltime, generate_time)
    SELECT
        COALESCE(end_time::DATE, create_time::DATE)                             AS s_execute_time,
        insert_time::DATE                                                       AS s_insert_time,
        machine_name_id                                                         AS s_machine_name_id,
        queue_id                                                                AS s_queue_id,
        global_user_name_id                                                     AS s_global_user_name_id,
        CASE WHEN global_user_name_id IS NULL THEN local_user_id ELSE NULL END  AS s_local_user_id,
        vo_information_id                                                       AS s_vo_information_id,
        CASE WHEN vo_information_id IS NULL THEN project_name_id ELSE NULL END  AS s_project_name_id,
        ARRAY(SELECT runtimeenvironment_usagedata.runtimeenvironments_id
              FROM runtimeenvironment_usagedata
              WHERE usagedata.id = runtimeenvironment_usagedata.usagedata_id)   AS s_runtime_environments,
        status_id                                                               AS s_status_id,
        insert_host_id                                                          AS s_insert_host_id,
        count(*)                                                                AS s_n_jobs,
        SUM(COALESCE(cpu_duration::bigint,0))                                   AS s_cputime,
        SUM(COALESCE(wall_duration::bigint,0) * COALESCE(processors,1))         AS s_walltime,
        now()                                                                   AS s_generate_time
    FROM
        usagedata
    WHERE
        insert_time::date = q_insert_date AND machine_name_id = q_machine_name_id
    GROUP BY
        s_execute_time, s_insert_time, s_machine_name_id, s_queue_id,
        s_global_user_name_id, s_local_user_id, s_vo_information_id, s_project_name_id,
        s_runtime_environments, s_status_id, s_insert_host_id;

    result[0] = q_insert_date::varchar;
    result[1] = q_machine_name_id;
    RETURN result;

END;
$insertdate_machinename$
LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION srcreate (
    in_record_id            varchar,
    in_create_time          timestamp,
    in_storage_system       varchar,
    in_storage_share        varchar,
    in_storage_media        varchar,
    in_storage_class        varchar,
    in_file_count           integer,
    in_directory_path       varchar,
    in_local_user           varchar,
    in_local_group          varchar,
    in_user_identity        varchar,
    in_group_identity       varchar,
    in_group_attribute      varchar[][],
    in_site                 varchar,
    in_start_time           timestamp,
    in_end_time             timestamp,
    in_resource_capacity_used   bigint,
    in_logical_capacity_used    bigint,
    in_insert_host          varchar,
    in_insert_identity      varchar,
    in_insert_time          timestamp
)
RETURNS
    varchar[] as $recordid_rowid$
DECLARE
    storage_system_key      integer;
    storage_share_key       integer;
    storage_media_key       integer;
    storage_class_key       integer;
    directory_path_key      integer;
    local_user_key          integer;
    local_group_key         integer;
    user_identity_key       integer;
    group_identity_key      integer;
    insert_host_key         integer;
    insert_identity_key     integer;
    site_key                integer;

    sr_key                  integer;
    result                  varchar[];
BEGIN
    -- first check if the record already exists
    SELECT storagedata.id INTO sr_key FROM storagedata WHERE record_id = in_record_id;
    IF FOUND THEN
        -- just return the entry from the already existing record
        result[0] = in_record_id;
        result[1] = sr_key;
        RETURN result;
    END IF;

    -- storage system
    IF in_storage_system IS NULL THEN
        RAISE EXCEPTION 'Storage system parameter must be non-null.';
    ELSE
        SELECT INTO storage_system_key id FROM storagesystem WHERE storage_system = in_storage_system;
        IF NOT FOUND THEN
            INSERT INTO storagesystem (storage_system) VALUES (in_storage_system) RETURNING id INTO storage_system_key;
        END IF;
    END IF;

    -- storage share
    IF in_storage_share IS NULL THEN
        storage_share_key = NULL;
    ELSE
        SELECT INTO storage_share_key id FROM storageshare WHERE storage_share = in_storage_share;
        IF NOT FOUND THEN
            INSERT INTO storageshare (storage_share) VALUES (in_storage_share) RETURNING id INTO storage_share_key;
        END IF;
    END IF;

    -- storage media
    IF in_storage_media IS NULL THEN
        storage_media_key = NULL;
    ELSE
        SELECT INTO storage_media_key id FROM storagemedia WHERE storage_media = in_storage_media;
        IF NOT FOUND THEN
            INSERT INTO storagemedia (storage_media) VALUES (in_storage_media) RETURNING id INTO storage_media_key;
        END IF;
    END IF;

    -- storage class
    IF in_storage_class IS NULL THEN
        storage_class_key = NULL;
    ELSE
        SELECT INTO storage_class_key id FROM storageclass WHERE storage_class = in_storage_class;
        IF NOT FOUND THEN
            INSERT INTO storageclass (storage_class) VALUES (in_storage_class) RETURNING id INTO storage_class_key;
        END IF;
    END IF;

    -- directory path
    IF in_directory_path IS NULL THEN
        directory_path_key = NULL;
    ELSE
        SELECT INTO directory_path_key id FROM directorypath WHERE directory_path = in_directory_path;
        IF NOT FOUND THEN
            INSERT INTO directorypath (directory_path) VALUES (in_directory_path) RETURNING id INTO directory_path_key;
        END IF;
    END IF;

    -- local user
    IF in_local_user IS NULL THEN
        local_user_key = NULL;
    ELSE
        SELECT INTO local_user_key id FROM localuser WHERE local_user = in_local_user;
        IF NOT FOUND THEN
            INSERT INTO localuser (local_user) VALUES (in_local_user) RETURNING id INTO local_user_key;
        END IF;
    END IF;

    -- local group
    IF in_local_group IS NULL THEN
        local_group_key = NULL;
    ELSE
        SELECT INTO local_group_key id FROM localgroup WHERE local_group = in_local_group;
        IF NOT FOUND THEN
            INSERT INTO localgroup (local_group) VALUES (in_local_group) RETURNING id INTO local_group_key;
        END IF;
    END IF;

    -- user identity
    IF in_user_identity IS NULL THEN
        user_identity_key = NULL;
    ELSE
        SELECT INTO user_identity_key id FROM useridentity WHERE user_identity = in_user_identity;
        IF NOT FOUND THEN
            INSERT INTO useridentity (user_identity) VALUES (in_user_identity) RETURNING id INTO user_identity_key;
        END IF;
    END IF;

    -- group identity
    IF in_group_identity IS NULL THEN
        group_identity_key = NULL;
    ELSE
        SELECT INTO group_identity_key id FROM groupidentity
               WHERE group_identity   IS NOT DISTINCT FROM in_group_identity AND
                     group_attribute  IS NOT DISTINCT FROM in_group_attribute;
        IF NOT FOUND THEN
            INSERT INTO groupidentity (group_identity, group_attribute) VALUES (in_group_identity, in_group_attribute) RETURNING id INTO group_identity_key;
        END IF;
    END IF;

    -- insert host
    IF in_insert_host IS NULL THEN
        insert_host_key = NULL;
    ELSE
        SELECT INTO insert_host_key id FROM inserthost WHERE insert_host = in_insert_host;
        IF NOT FOUND THEN
            INSERT INTO inserthost (insert_host) VALUES (in_insert_host) RETURNING id INTO insert_host_key;
        END IF;
    END IF;

    -- insert identity
    IF in_insert_identity IS NULL THEN
        insert_identity_key = NULL;
    ELSE
        SELECT INTO insert_identity_key id FROM insertidentity WHERE insert_identity = in_insert_identity;
        IF NOT FOUND THEN
            INSERT INTO insertidentity (insert_identity) VALUES (in_insert_identity) RETURNING id INTO insert_identity_key;
        END IF;
    END IF;

    -- insert identity
    IF in_site IS NULL THEN
        site_key = NULL;
    ELSE
        SELECT INTO site_key id FROM site WHERE site = in_site;
        IF NOT FOUND THEN
            INSERT INTO site (site) VALUES (in_site) RETURNING id INTO site_key;
        END IF;
    END IF;

    INSERT INTO storagedata (
                    record_id,
                    create_time,
                    storage_system_id,
                    storage_share_id,
                    storage_media_id,
                    storage_class_id,
                    file_count,
                    directory_path_id,
                    local_user_id,
                    local_group_id,
                    user_identity_id,
                    group_identity_id,
                    site_id,
                    start_time,
                    end_time,
                    resource_capacity_used,
                    logical_capacity_used,
                    insert_host_id,
                    insert_identity_id,
                    insert_time
            )
            VALUES (
                    in_record_id,
                    in_create_time,
                    storage_system_key,
                    storage_share_key,
                    storage_media_key,
                    storage_class_key,
                    in_file_count,
                    directory_path_key,
                    local_user_key,
                    local_group_key,
                    user_identity_key,
                    group_identity_key,
                    site_key,
                    in_start_time,
                    in_end_time,
                    in_resource_capacity_used,
                    in_logical_capacity_used,
                    insert_host_key,
                    insert_identity_key,
                    in_insert_time
                    )
            RETURNING id INTO sr_key;

    result[0] = in_record_id;
    result[1] = sr_key;
    RETURN result;

END;
$recordid_rowid$
LANGUAGE plpgsql;

