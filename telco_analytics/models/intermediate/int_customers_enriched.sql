with customers as (

    select * from {{ ref('stg_telco__customers') }}

),

enriched as (

    select
        -- Keys
        customer_id,

        -- Demographics (pass-through)
        gender,
        is_senior_citizen,
        has_partner,
        has_dependents,

        -- Tenure + bucket
        tenure_months::integer                          as tenure_months,
        case
            when tenure_months::integer between 0  and 6  then '0-6 months'
            when tenure_months::integer between 7  and 12 then '7-12 months'
            when tenure_months::integer between 13 and 24 then '13-24 months'
            when tenure_months::integer between 25 and 48 then '25-48 months'
            else '49+ months'
        end                                             as tenure_bucket,
        case
            when tenure_months::integer between 0  and 6  then 1
            when tenure_months::integer between 7  and 12 then 2
            when tenure_months::integer between 13 and 24 then 3
            when tenure_months::integer between 25 and 48 then 4
            else 5
        end                                             as tenure_bucket_order,

        -- Contract & billing (pass-through)
        contract_type,
        has_paperless_billing,
        payment_method,

        -- Charges
        monthly_charges::numeric                        as monthly_charges,
        total_charges::numeric                          as total_charges,
        case
            when monthly_charges::numeric < 30  then 'low'
            when monthly_charges::numeric < 65  then 'medium'
            when monthly_charges::numeric < 90  then 'high'
            else 'very high'
        end                                             as monthly_charge_tier,

        -- Lifetime value proxy
        round(
            coalesce(
                total_charges::numeric,
                monthly_charges::numeric * tenure_months::integer
            ), 2
        )                                               as lifetime_value,

        -- Service flags (pass-through)
        has_phone_service,
        has_multiple_lines,
        has_internet_service,
        internet_service_type,
        has_online_security,
        has_online_backup,
        has_device_protection,
        has_tech_support,
        has_streaming_tv,
        has_streaming_movies,

        -- Service count
        (
            coalesce(has_multiple_lines::int,    0) +
            coalesce(has_online_security::int,   0) +
            coalesce(has_online_backup::int,     0) +
            coalesce(has_device_protection::int, 0) +
            coalesce(has_tech_support::int,      0) +
            coalesce(has_streaming_tv::int,      0) +
            coalesce(has_streaming_movies::int,  0)
        )                                               as addon_service_count,

        -- High value flag
        case
            when monthly_charges::numeric >= 65
            and coalesce(has_multiple_lines::int,    0) +
                coalesce(has_online_security::int,   0) +
                coalesce(has_online_backup::int,     0) +
                coalesce(has_device_protection::int, 0) +
                coalesce(has_tech_support::int,      0) +
                coalesce(has_streaming_tv::int,      0) +
                coalesce(has_streaming_movies::int,  0) >= 2
            then true
            else false
        end                                             as is_high_value,

        -- Target
        has_churned

    from customers

)

select * from enriched