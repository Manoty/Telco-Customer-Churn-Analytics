with source as (

    select * from {{ source('raw', 'telco_churn') }}

),

renamed as (

    select
        -- Primary key
        customerid                                          as customer_id,

        -- Demographics
        gender,
        case when seniorcitizen = 1 then true else false end    as is_senior_citizen,
        case when partner = 'Yes' then true else false end      as has_partner,
        case when dependents = 'Yes' then true else false end   as has_dependents,

        -- Tenure
        tenure                                              as tenure_months,

        -- Phone services
        case when phoneservice = 'Yes' then true else false end as has_phone_service,
        case
            when multiplelines = 'Yes' then true
            when multiplelines = 'No' then false
            else null  -- 'No phone service' → not eligible
        end                                                 as has_multiple_lines,

        -- Internet services
        case
            when internetservice = 'No' then false
            else true
        end                                                 as has_internet_service,
        internetservice                                     as internet_service_type,

        case
            when onlinesecurity = 'Yes' then true
            when onlinesecurity = 'No' then false
            else null  -- 'No internet service' → not eligible
        end                                                 as has_online_security,

        case
            when onlinebackup = 'Yes' then true
            when onlinebackup = 'No' then false
            else null
        end                                                 as has_online_backup,

        case
            when deviceprotection = 'Yes' then true
            when deviceprotection = 'No' then false
            else null
        end                                                 as has_device_protection,

        case
            when techsupport = 'Yes' then true
            when techsupport = 'No' then false
            else null
        end                                                 as has_tech_support,

        case
            when streamingtv = 'Yes' then true
            when streamingtv = 'No' then false
            else null
        end                                                 as has_streaming_tv,

        case
            when streamingmovies = 'Yes' then true
            when streamingmovies = 'No' then false
            else null
        end                                                 as has_streaming_movies,

        -- Contract & billing
        contract                                            as contract_type,
        case when paperlessbilling = 'Yes' then true else false end as has_paperless_billing,
        paymentmethod                                       as payment_method,

        -- Charges
        monthlycharges                                      as monthly_charges,
        nullif(trim(totalcharges), '')::numeric             as total_charges,

        -- Target variable
        case when churn = 'Yes' then true else false end    as has_churned

    from source

)

select * from renamed