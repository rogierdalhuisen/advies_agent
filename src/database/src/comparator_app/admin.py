from django.contrib import admin
from .models import (
    Landen,
    Relaties,
    Personen,
    AdviesAanvragen,
    AdviesAanvraagEngels,
    AdviesAanvraagBelgie,
    AdviesAanvraagWoning,
    OfferteArbeidsOngeschiktheid,
    AllianzCareQuote,
    Contracten,
    VerzekeringRegio,
    VerzekeringRegioLanden,
    DoelGroepen,
    Verzekeringen,
    VerzekeringDoelGroepen,
    VerzekeringModules,
    BedrijfsRegels
)


# --- Support Tables Admin ---
@admin.register(Landen)
class LandenAdmin(admin.ModelAdmin):
    list_display = ('land_code', 'land_naam')
    search_fields = ('land_naam', 'land_code')


@admin.register(DoelGroepen)
class DoelGroepenAdmin(admin.ModelAdmin):
    list_display = ('doelgroep_id', 'doelgroep_naam')
    search_fields = ('doelgroep_naam',)


# --- Relatie-gerelateerde Admin ---
class PersonenInline(admin.TabularInline):
    model = Personen
    extra = 0
    fields = ('api_persoon_id', 'persoon_naam', 'persoon_email')
    show_change_link = True


@admin.register(Relaties)
class RelatiesAdmin(admin.ModelAdmin):
    list_display = ('relatie_id', 'hoofdnaam', 'get_email_display', 'has_api_link', 'aangemaakt_op')
    search_fields = ('hoofdnaam', 'relatie_id')
    list_filter = ('aangemaakt_op',)
    date_hierarchy = 'aangemaakt_op'
    inlines = [PersonenInline]

    def has_api_link(self, obj):
        return obj.relatie_id is not None
    has_api_link.short_description = 'API Linked'
    has_api_link.boolean = True

    def get_email_display(self, obj):
        if obj.email_adressen:
            return ', '.join(obj.email_adressen[:2])  # Show first 2 emails
        return 'Geen email'
    get_email_display.short_description = 'Email Adressen'


@admin.register(Personen)
class PersonenAdmin(admin.ModelAdmin):
    list_display = ('persoon_id', 'persoon_naam', 'persoon_email', 'relatie', 'api_persoon_id')
    search_fields = ('persoon_naam', 'persoon_email', 'relatie__hoofdnaam')
    list_filter = ('relatie',)


@admin.register(AdviesAanvragen)
class AdviesAanvragenAdmin(admin.ModelAdmin):
    list_display = (
        'aanvraag_id',
        'get_naam',
        'email',
        'bestemming_land',
        'huidig_woonland',
        'vertrekdatum',
        'interesse_zkv',
        'ingediend_op'
    )
    list_filter = (
        'interesse_zkv',
        'interesse_aov',
        'bestemming_land',
        'huidig_woonland',
        'situatie_type',
        'referral_source',
        'ingediend_op'
    )
    search_fields = (
        'email',
        'voorletters_roepnaam',
        'achternaam',
        'relatie__hoofdnaam',
        'external_result_id'
    )
    date_hierarchy = 'ingediend_op'
    readonly_fields = ('external_result_id', 'form_id', 'aangemaakt_op', 'raw_form_data')

    fieldsets = (
        ('Metadata', {
            'fields': ('aanvraag_id', 'external_result_id', 'form_id', 'relatie', 'ingediend_op', 'aangemaakt_op')
        }),
        ('Persoonlijke Gegevens', {
            'fields': (
                'advies_voor_mezelf',
                'aanhef',
                'voorletters_roepnaam',
                'achternaam',
                'geboortedatum',
                'land_nationaliteit',
                'email',
                'telefoonnummer',
                'vaste_woonplaats',
            )
        }),
        ('Familie/Meerdere Verzekerden', {
            'fields': (
                'meerdere_verzekerden',
                'partner_naam',
                'partner_geboortedatum',
                'partner_nationaliteit',
                'kind1_naam',
                'kind1_geboortedatum',
                'kind2_naam',
                'kind2_geboortedatum',
                'kind3_naam',
                'kind3_geboortedatum',
                'kind4_naam',
                'kind4_geboortedatum',
            ),
            'classes': ('collapse',)
        }),
        ('Situatie & Plannen', {
            'fields': (
                'situatie_type',
                'bestemming_land',
                'vertrekdatum',
                'huidig_woonland',
                'uitschrijven_brp',
                'hoofdreden_verblijf',
                'toelichting_hoofdreden',
                'verwachte_duur_verblijf',
                'toelichting_duur',
            )
        }),
        ('Verzekeringen', {
            'fields': (
                'interesse_zkv',
                'zkv_dekkingsvariant',
                'zkv_eigen_risico_voorkeur',
                'zkv_periode',
                'interesse_aov',
                'interesse_internationale_aov',
                'andere_verzekeringen_interesse',
            )
        }),
        ('Werk & Inkomen', {
            'fields': (
                'werk_omschrijving',
                'loondienst_of_zelfstandig',
                'bruto_salaris_inkomen',
                'salaris_per_maand_jaar',
            ),
            'classes': ('collapse',)
        }),
        ('Medisch', {
            'fields': (
                'medische_bijzonderheden',
                'medische_bijzonderheden_toelichting',
            ),
            'classes': ('collapse',)
        }),
        ('Marketing', {
            'fields': (
                'referral_source',
                'referral_medium',
                'referral_campaign',
                'hoe_gevonden',
                'welke_website',
            ),
            'classes': ('collapse',)
        }),
        ('Raw Data (Backup)', {
            'fields': ('raw_form_data',),
            'classes': ('collapse',)
        }),
    )

    def get_naam(self, obj):
        """Combineer voornaam en achternaam."""
        naam = f"{obj.voorletters_roepnaam or ''} {obj.achternaam or ''}".strip()
        return naam if naam else '-'
    get_naam.short_description = 'Naam'
    get_naam.admin_order_field = 'achternaam'


@admin.register(AdviesAanvraagEngels)
class AdviesAanvraagEngelsAdmin(admin.ModelAdmin):
    list_display = (
        'aanvraag_id',
        'get_naam',
        'email',
        'bestemming_land',
        'vertrekdatum',
        'interesse_zkv',
        'ingediend_op'
    )
    list_filter = (
        'interesse_zkv',
        'interesse_aov',
        'bestemming_land',
        'referral_source',
        'ingediend_op'
    )
    search_fields = (
        'email',
        'voorletters_roepnaam',
        'achternaam',
        'relatie__hoofdnaam',
        'external_result_id'
    )
    date_hierarchy = 'ingediend_op'
    readonly_fields = ('external_result_id', 'form_id', 'aangemaakt_op', 'raw_form_data')

    fieldsets = (
        ('Metadata', {
            'fields': ('aanvraag_id', 'external_result_id', 'form_id', 'relatie', 'ingediend_op', 'aangemaakt_op')
        }),
        ('Personal Data', {
            'fields': (
                'advies_voor_mezelf',
                'aanhef',
                'voorletters_roepnaam',
                'achternaam',
                'geboortedatum',
                'land_nationaliteit',
                'email',
                'telefoonnummer',
                'vaste_woonplaats',
            )
        }),
        ('Multiple Insured Persons', {
            'fields': ('meerdere_verzekerden',),
            'classes': ('collapse',)
        }),
        ('Abroad / Situation', {
            'fields': (
                'bestemming_land',
                'verwachte_duur_verblijf',
                'vertrekdatum',
                'vertrek_wanneer',
                'verwachte_vertrekdatum',
                'hoofdreden_verblijf',
            )
        }),
        ('Work', {
            'fields': (
                'werk_omschrijving',
                'plannen_omschrijving',
            ),
            'classes': ('collapse',)
        }),
        ('Income Protection Insurance', {
            'fields': (
                'interesse_aov',
                'loondienst_of_zelfstandig',
                'bruto_jaarinkomen',
                'bruto_salaris_inkomen',
            ),
            'classes': ('collapse',)
        }),
        ('Health Insurance', {
            'fields': (
                'interesse_zkv',
                'zkv_periode',
                'zkv_periode_omschrijving_motivatie',
                'zkv_periode_omschrijving',
                'huidige_verzekeraar',
                'voorkeur_verzekeraar',
                'medische_bijzonderheden',
                'medische_bijzonderheden_toelichting',
                'specifieke_wensen_zkv',
                'wensen_toelichting',
                'dekking_zwangerschap',
                'zwangerschap_toelichting',
            )
        }),
        ('Additional Insurances', {
            'fields': ('andere_verzekeringen_interesse',),
            'classes': ('collapse',)
        }),
        ('Remarks', {
            'fields': ('opmerkingen',),
            'classes': ('collapse',)
        }),
        ('Marketing', {
            'fields': (
                'referral_source',
                'referral_medium',
                'referral_campaign',
            ),
            'classes': ('collapse',)
        }),
        ('Raw Data (Backup)', {
            'fields': ('raw_form_data',),
            'classes': ('collapse',)
        }),
    )

    def get_naam(self, obj):
        """Combine first name and surname."""
        naam = f"{obj.voorletters_roepnaam or ''} {obj.achternaam or ''}".strip()
        return naam if naam else '-'
    get_naam.short_description = 'Naam'
    get_naam.admin_order_field = 'achternaam'


@admin.register(AdviesAanvraagBelgie)
class AdviesAanvraagBelgieAdmin(admin.ModelAdmin):
    list_display = (
        'aanvraag_id',
        'get_naam',
        'email',
        'bestemming_land',
        'vertrekdatum',
        'interesse_zkv',
        'interesse_aov',
        'ingediend_op'
    )
    list_filter = (
        'interesse_zkv',
        'interesse_aov',
        'bestemming_land',
        'referral_source',
        'ingediend_op'
    )
    search_fields = (
        'email',
        'voorletters_roepnaam',
        'achternaam',
        'relatie__hoofdnaam',
        'external_result_id'
    )
    date_hierarchy = 'ingediend_op'
    readonly_fields = ('external_result_id', 'form_id', 'aangemaakt_op', 'raw_form_data')

    fieldsets = (
        ('Metadata', {
            'fields': ('aanvraag_id', 'external_result_id', 'form_id', 'relatie', 'ingediend_op', 'aangemaakt_op')
        }),
        ('Persoonlijke Gegevens', {
            'fields': (
                'advies_voor_mezelf',
                'aanhef',
                'voorletters_roepnaam',
                'achternaam',
                'geboortedatum',
                'land_nationaliteit',
                'email',
                'telefoonnummer',
                'vaste_woonplaats',
            )
        }),
        ('Meerdere Verzekerden', {
            'fields': ('meerdere_verzekerden',),
            'classes': ('collapse',)
        }),
        ('Situatie & Plannen', {
            'fields': (
                'bestemming_land',
                'verwachte_duur_verblijf',
                'vertrekdatum',
                'vertrek_wanneer',
                'verwachte_vertrekdatum',
                'hoofdreden_verblijf',
            )
        }),
        ('Werk & Inkomen', {
            'fields': (
                'werk_omschrijving',
                'plannen_omschrijving',
                'salaris_uit_belgie',
            ),
            'classes': ('collapse',)
        }),
        ('AOV', {
            'fields': (
                'interesse_aov',
                'loondienst_of_zelfstandig',
                'eigen_onderneming_3jaar',
                'bruto_jaarinkomen',
                'aov_geen_offerte_reden',
                'loon_doorbetaald_bij_ziekte',
                'toelichting_uitkering',
                'bruto_salaris_inkomen',
                'salaris_per_maand_jaar',
                'bouwplaats_of_offshore',
                'bouwplaats_hoe_vaak',
                'gevaarlijke_stoffen',
                'toelichting_gevaarlijke_stoffen',
            ),
            'classes': ('collapse',)
        }),
        ('Ziektekostenverzekering', {
            'fields': (
                'interesse_zkv',
                'zkv_geen_interesse_reden',
                'zkv_dekkingsvariant',
                'zkv_eigen_risico_voorkeur',
                'zkv_eigen_risico_bedrag',
                'zkv_periode',
                'zkv_periode_omschrijving_motivatie',
                'zkv_periode_omschrijving',
                'huidige_verzekeraar',
                'voorkeur_verzekeraar',
                'medische_bijzonderheden',
                'medische_bijzonderheden_toelichting',
                'specifieke_wensen_zkv',
                'wensen_toelichting',
                'dekking_zwangerschap',
                'zwangerschap_toelichting',
            )
        }),
        ('Sporten & Activiteiten', {
            'fields': (
                'sporten_activiteiten',
                'sport_semiprofessioneel',
                'sport_professioneel_omschrijving',
            ),
            'classes': ('collapse',)
        }),
        ('Aanvullende Verzekeringen', {
            'fields': (
                'andere_verzekeringen_interesse',
                'overlijdensrisico_bedrag',
                'overlijdensrisico_bedrag_anders',
                'overlijdensrisico_bestemming',
                'overlijdensrisico_bestemming_anders',
            ),
            'classes': ('collapse',)
        }),
        ('Opmerkingen', {
            'fields': ('opmerkingen',),
            'classes': ('collapse',)
        }),
        ('Marketing & Contact', {
            'fields': (
                'referral_source',
                'referral_medium',
                'referral_campaign',
                'hoe_gevonden',
                'welke_website',
                'naam_werkgever',
                'hoe_gevonden_overig',
                'eerder_contact_joho',
                'eerder_contact_keuze',
                'naam_contactpersoon',
                'eerder_contact_anders',
                'advies_vorm',
            ),
            'classes': ('collapse',)
        }),
        ('Raw Data (Backup)', {
            'fields': ('raw_form_data',),
            'classes': ('collapse',)
        }),
    )

    def get_naam(self, obj):
        """Combineer voornaam en achternaam."""
        naam = f"{obj.voorletters_roepnaam or ''} {obj.achternaam or ''}".strip()
        return naam if naam else '-'
    get_naam.short_description = 'Naam'
    get_naam.admin_order_field = 'achternaam'


@admin.register(AdviesAanvraagWoning)
class AdviesAanvraagWoningAdmin(admin.ModelAdmin):
    list_display = (
        'aanvraag_id',
        'get_naam',
        'email',
        'woning_postcode_plaats',
        'soort_woning',
        'woonland_buitenland',
        'ingediend_op'
    )
    list_filter = (
        'soort_woning',
        'woning_land',
        'woonland_buitenland',
        'uitgeschreven_brp',
        'referral_source',
        'ingediend_op'
    )
    search_fields = (
        'email',
        'voornaam',
        'achternaam',
        'woning_postcode_plaats',
        'woning_straat_huisnummer',
        'relatie__hoofdnaam',
        'external_result_id'
    )
    date_hierarchy = 'ingediend_op'
    readonly_fields = ('external_result_id', 'form_id', 'aangemaakt_op', 'raw_form_data')

    fieldsets = (
        ('Metadata', {
            'fields': ('aanvraag_id', 'external_result_id', 'form_id', 'relatie', 'ingediend_op', 'aangemaakt_op')
        }),
        ('Gegevens Aanvrager', {
            'fields': (
                'voornaam',
                'achternaam',
                'geboortedatum',
                'geslacht',
                'email',
                'telefoonnummer',
                'nationaliteit',
                'woonland_buitenland',
                'correspondentie_adres_nl',
                'vertrekdatum',
                'uitgeschreven_brp',
            )
        }),
        ('Gegevens Woning', {
            'fields': (
                'woning_straat_huisnummer',
                'woning_postcode_plaats',
                'woning_land',
                'woning_gebruik',
                'woning_gebruik_extra',
                'soort_woning',
                'bouwaard',
                'dakbedekking',
                'bijzonderheden_woning',
                'woning_extra_info',
            )
        }),
        ('Verzekeringen Woning', {
            'fields': (
                'interesse_verzekeringen',
                'gewenste_startdatum',
            )
        }),
        ('Verzekeringen Buitenland', {
            'fields': ('interesse_internationale_verzekeringen',),
            'classes': ('collapse',)
        }),
        ('Opmerkingen', {
            'fields': ('opmerkingen',),
            'classes': ('collapse',)
        }),
        ('Marketing', {
            'fields': (
                'referral_source',
                'referral_medium',
                'referral_campaign',
            ),
            'classes': ('collapse',)
        }),
        ('Raw Data (Backup)', {
            'fields': ('raw_form_data',),
            'classes': ('collapse',)
        }),
    )

    def get_naam(self, obj):
        """Combineer voornaam en achternaam."""
        naam = f"{obj.voornaam or ''} {obj.achternaam or ''}".strip()
        return naam if naam else '-'
    get_naam.short_description = 'Naam'
    get_naam.admin_order_field = 'achternaam'


@admin.register(OfferteArbeidsOngeschiktheid)
class OfferteArbeidsOngeschiktheidAdmin(admin.ModelAdmin):
    list_display = (
        'aanvraag_id',
        'get_naam',
        'email',
        'bestemming_land',
        'vertrekdatum',
        'loondienst_of_zelfstandig',
        'ingediend_op'
    )
    list_filter = (
        'loondienst_of_zelfstandig',
        'bestemming_land',
        'interesse_zkv',
        'interesse_levensverzekering',
        'referral_source',
        'ingediend_op'
    )
    search_fields = (
        'email',
        'voorletters',
        'achternaam',
        'relatie__hoofdnaam',
        'external_result_id'
    )
    date_hierarchy = 'ingediend_op'
    readonly_fields = ('external_result_id', 'form_id', 'aangemaakt_op', 'raw_form_data')

    fieldsets = (
        ('Metadata', {
            'fields': ('aanvraag_id', 'external_result_id', 'form_id', 'relatie', 'ingediend_op', 'aangemaakt_op')
        }),
        ('Persoonlijke Gegevens', {
            'fields': (
                'geslacht',
                'achternaam',
                'voorletters',
                'geboortedatum',
                'telefoonnummer',
                'email',
                'nationaliteit',
            )
        }),
        ('Bestemming & Vertrek', {
            'fields': (
                'bestemming_land',
                'vertrekdatum',
                'vertrek_wanneer',
                'verwachte_vertrekdatum',
                'verwachte_duur_verblijf',
            )
        }),
        ('Werk & Inkomen', {
            'fields': (
                'bruto_jaarinkomen',
                'jaarrente_verzekerd_bedrag',
                'werk_omschrijving',
                'werkzaamheden',
                'salaris_uit_nederland',
                'loondienst_of_zelfstandig',
                'eigen_onderneming_3jaar',
                'loon_doorbetaald_bij_ziekte',
                'toelichting_uitkering',
            )
        }),
        ('Werkomstandigheden', {
            'fields': (
                'bouwplaats_of_offshore',
                'bouwplaats_hoe_vaak',
                'reist_veel_voor_werk',
                'frequentie_vervoersmiddel',
                'gevaarlijke_stoffen',
                'toelichting_gevaarlijke_stoffen',
            ),
            'classes': ('collapse',)
        }),
        ('Ziektekostenverzekering', {
            'fields': (
                'interesse_zkv',
                'ziektekosten',
                'huidige_verzekeraar_ziektekosten',
            ),
            'classes': ('collapse',)
        }),
        ('Levensverzekering', {
            'fields': (
                'interesse_levensverzekering',
                'levensverzekering',
                'rookt',
                'gewenste_verzekerde_som',
            ),
            'classes': ('collapse',)
        }),
        ('Opmerkingen', {
            'fields': ('opmerkingen', 'opmerkingen_2'),
            'classes': ('collapse',)
        }),
        ('Marketing', {
            'fields': (
                'referral_source',
                'referral_medium',
                'referral_campaign',
                'hoe_gevonden',
            ),
            'classes': ('collapse',)
        }),
        ('Raw Data (Backup)', {
            'fields': ('raw_form_data',),
            'classes': ('collapse',)
        }),
    )

    def get_naam(self, obj):
        """Combineer voorletters en achternaam."""
        naam = f"{obj.voorletters or ''} {obj.achternaam or ''}".strip()
        return naam if naam else '-'
    get_naam.short_description = 'Naam'
    get_naam.admin_order_field = 'achternaam'


@admin.register(AllianzCareQuote)
class AllianzCareQuoteAdmin(admin.ModelAdmin):
    list_display = (
        'aanvraag_id',
        'get_naam',
        'email',
        'destination',
        'start_date',
        'area_of_cover',
        'ingediend_op'
    )
    list_filter = (
        'area_of_cover',
        'destination',
        'current_country',
        'referral_source',
        'ingediend_op'
    )
    search_fields = (
        'email',
        'first_name',
        'last_name',
        'destination',
        'relatie__hoofdnaam',
        'external_result_id'
    )
    date_hierarchy = 'ingediend_op'
    readonly_fields = ('external_result_id', 'form_id', 'aangemaakt_op', 'raw_form_data')

    fieldsets = (
        ('Metadata', {
            'fields': ('aanvraag_id', 'external_result_id', 'form_id', 'relatie', 'ingediend_op', 'aangemaakt_op')
        }),
        ('Personal Data', {
            'fields': (
                'first_name',
                'last_name',
                'gender',
                'email',
                'geboortedatum',
                'nationaliteit',
            )
        }),
        ('Family Members', {
            'fields': ('family_members',),
            'classes': ('collapse',)
        }),
        ('Location & Stay', {
            'fields': (
                'country_of_origin',
                'current_country',
                'destination',
                'purpose_of_stay',
                'expected_duration',
            )
        }),
        ('Coverage', {
            'fields': (
                'area_of_cover',
                'start_date',
                'cover_inpatient',
                'deductible_inpatient',
                'deductible_outpatient',
            )
        }),
        ('Remarks', {
            'fields': ('opmerkingen',),
            'classes': ('collapse',)
        }),
        ('Marketing', {
            'fields': (
                'referral_source',
                'referral_medium',
                'referral_campaign',
            ),
            'classes': ('collapse',)
        }),
        ('Raw Data (Backup)', {
            'fields': ('raw_form_data',),
            'classes': ('collapse',)
        }),
    )

    def get_naam(self, obj):
        """Combine first name and last name."""
        naam = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return naam if naam else '-'
    get_naam.short_description = 'Naam'
    get_naam.admin_order_field = 'last_name'


@admin.register(Contracten)
class ContractenAdmin(admin.ModelAdmin):
    list_display = ('contract_id', 'polisnummer', 'omschrijving', 'get_relatie_display', 'get_relatie_id', 'branche', 'datum_ingang', 'ts_aangemaakt')
    list_filter = ('branche', 'datum_ingang')
    search_fields = ('polisnummer', 'omschrijving', 'relatie__hoofdnaam', 'relatie__relatie_id')
    date_hierarchy = 'datum_ingang'

    def get_relatie_display(self, obj):
        """Display relation name."""
        return obj.relatie.hoofdnaam or 'Geen naam'
    get_relatie_display.short_description = 'Relatie Naam'
    get_relatie_display.admin_order_field = 'relatie__hoofdnaam'

    def get_relatie_id(self, obj):
        """Display Assuportal relatie_id."""
        return obj.relatie.relatie_id or '-'
    get_relatie_id.short_description = 'Relatie ID (Assuportal)'
    get_relatie_id.admin_order_field = 'relatie__relatie_id'


# --- Verzekering Regio & Verzekering Admin ---
@admin.register(VerzekeringRegio)
class VerzekeringRegioAdmin(admin.ModelAdmin):
    list_display = ('verzekering_regio_id', 'verzekeraar_naam', 'regio_naam', 'status', 'get_verzekeringen_count', 'get_landen_count')
    list_filter = ('status', 'verzekeraar_naam')
    search_fields = ('verzekeraar_naam', 'regio_naam')

    def get_verzekeringen_count(self, obj):
        count = obj.verzekeringen.count()
        if count == 0:
            return '0 verzekeringen'
        return f'{count} verzekeringen'
    get_verzekeringen_count.short_description = 'Verzekeringen'

    def get_landen_count(self, obj):
        count = obj.regio_landen.count()
        if count == 0:
            return '0 landen'
        return f'{count} landen'
    get_landen_count.short_description = 'Landen'


@admin.register(VerzekeringRegioLanden)
class VerzekeringRegioLandenAdmin(admin.ModelAdmin):
    list_display = ('get_verzekeraar_regio', 'get_land_naam')
    list_filter = ('verzekering_regio__verzekeraar_naam',)
    search_fields = ('land_code__land_naam', 'verzekering_regio__verzekeraar_naam', 'verzekering_regio__regio_naam')

    def get_verzekeraar_regio(self, obj):
        """Display verzekeraar and regio name."""
        return f"{obj.verzekering_regio.verzekeraar_naam} - {obj.verzekering_regio.regio_naam}"
    get_verzekeraar_regio.short_description = 'Verzekering Regio'
    get_verzekeraar_regio.admin_order_field = 'verzekering_regio__verzekeraar_naam'

    def get_land_naam(self, obj):
        """Display country name."""
        return obj.land_code.land_naam
    get_land_naam.short_description = 'Land'
    get_land_naam.admin_order_field = 'land_code__land_naam'


# --- Verzekering Admin with Inlines ---
class VerzekeringModulesInline(admin.TabularInline):
    model = VerzekeringModules
    extra = 0
    fields = ('verzekeraar_specifieke_naam', 'is_verplicht')
    show_change_link = True


class VerzekeringDoelGroepenInline(admin.TabularInline):
    model = VerzekeringDoelGroepen
    extra = 1
    verbose_name = 'Doelgroep'
    verbose_name_plural = 'Doelgroepen'


@admin.register(Verzekeringen)
class VerzekeringenAdmin(admin.ModelAdmin):
    list_display = (
        'verzekering_id',
        'naam',
        'verzekering_regio',
        'polis_type',
        'get_modules_count',
        'get_doelgroepen_count',
        'max_leeftijd_aanvraag',
        'max_leeftijd_dekking'
    )
    list_filter = ('verzekering_regio__verzekeraar_naam', 'polis_type')
    search_fields = ('naam', 'omschrijving')
    inlines = [VerzekeringDoelGroepenInline, VerzekeringModulesInline]

    def get_modules_count(self, obj):
        count = obj.verzekering_modules.count()
        if count == 0:
            return '0 modules'
        return f'{count} modules'
    get_modules_count.short_description = 'Modules'

    def get_doelgroepen_count(self, obj):
        count = obj.doelgroep_koppelingen.count()
        if count == 0:
            return 'Geen'
        return f'{count}'
    get_doelgroepen_count.short_description = 'Doelgroepen'


@admin.register(VerzekeringModules)
class VerzekeringModulesAdmin(admin.ModelAdmin):
    list_display = (
        'verzekering_module_id',
        'verzekering',
        'verzekeraar_specifieke_naam',
        'is_verplicht'
    )
    list_filter = ('verzekering', 'is_verplicht')
    search_fields = ('verzekeraar_specifieke_naam',)


@admin.register(VerzekeringDoelGroepen)
class VerzekeringDoelGroepenAdmin(admin.ModelAdmin):
    list_display = ('verzekering', 'doelgroep')
    list_filter = ('verzekering', 'doelgroep')
    search_fields = ('verzekering__naam', 'doelgroep__doelgroep_naam')


# --- Business Rules Admin ---
@admin.register(BedrijfsRegels)
class BedrijfsRegelsAdmin(admin.ModelAdmin):
    list_display = ('regel_id', 'bereik_entiteit', 'bereik_id', 'regel_type')
    list_filter = ('bereik_entiteit', 'regel_type')
    search_fields = ('bericht',)
