with source as (

    select * from {{ source('networkrail', 'movements') }}

),

renamed_recasted as (

    select
        event_type
        , gbtt_timestamp
        , original_loc_stanox
        , planned_timestamp
        , timetable_variation
        , original_loc_timestamp
        , current_train_id
        , delay_monitoring_point
        , next_report_run_time
        , reporting_stanox
        , actual_timestamp
        , correction_ind
        , event_source
        , train_file_address
        , platform
        , division_code
        , train_terminated
        , train_id
        , offroute_ind
        , variation_status
        , train_service_code
        , toc_id
        , loc_stanox
        , auto_expected
        , direction_ind
        , route
        , planned_event_type
        , next_report_stanox
        , line_ind

    from source

)

select * from renamed_recasted