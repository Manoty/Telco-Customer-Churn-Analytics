with enriched as (

    select * from {{ ref('int_customers_enriched') }}

),

final as (

    select
        -- Primary key
        customer_id,

        -- Demographics
        gender,
        is_senior_citizen,
        has_partner,
        has_dependents,

        -- Tenure
        tenure_months,
        tenure_bucket,
        tenure_bucket_order,

        -- Contract & billing
        contract_type,
        has_paperless_billing,
        payment_method,

        -- Charges profile
        monthly_charges,
        total_charges,
        monthly_charge_tier,
        lifetime_value,

        -- Service profile
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
        addon_service_count,
        is_high_value

    from enriched

)

select * from final