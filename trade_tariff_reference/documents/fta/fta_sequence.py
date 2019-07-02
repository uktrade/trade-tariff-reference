import glob as g
import functions as f

# Set up
app = g.app
for item in app.all_country_profiles:
    produce_schedule = app.all_country_profiles[item]["produce_schedule"]
    if produce_schedule:
        app.country_profile = item
        app.get_country_list()
        app.geo_ids = f.list_to_sql(app.country_codes)
        app.create_document()

app.shutDown()
print("\nPROCESS COMPLETE")
