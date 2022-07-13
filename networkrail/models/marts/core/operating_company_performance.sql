with

movements as (

    select
        actual_timestamp
        , {{ get_toc_names() }} as train_operating_company
        , variation_status

    from {{ ref('stg_networkrail__movements') }}

)

select * from movements