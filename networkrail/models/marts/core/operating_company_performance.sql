with

movements as (

    select
        actual_timestamp
        , case
            when toc_id = '20' then 'TransPennine Express'
            when toc_id = '23' then 'Arriva Trains Northern'
            when toc_id = '28' then 'East Midlands Trains'
            when toc_id = '29' then 'West Midlands Trains'
            when toc_id = '61' then 'London North Eastern Railway'
            when toc_id = '71' then 'Transport for Wales'
            when toc_id = '80' then 'Southeastern'
            when toc_id = '88' then 'Govia Thameslink Railway (Thameslink)'
            else 'Unknown'
            end as train_operating_company
        , variation_status

    from {{ ref('stg_networkrail__movements') }}

)

select * from movements