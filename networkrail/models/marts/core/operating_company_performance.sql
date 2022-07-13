with

movements as (

    select
        actual_timestamp
        , toc_id
        , variation_status

    from {{ ref('stg_networkrail__movements') }}

)

select * from movements