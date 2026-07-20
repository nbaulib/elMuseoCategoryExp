from pathlib import Path
import pandas as pd
import streamlit as st
import zipfile
import io

CATEGORY_COLUMN = "Categories"
EMAIL_COLUMN = "Email/Contact Info"

st.title("Press List Category Exporter")

uploaded_file = st.file_uploader(
    "Upload Excel file",
    type=["xlsx"]
)

if uploaded_file:

    df = pd.read_excel(
        uploaded_file,
        sheet_name=0
    )

    # remove empty rows
    df = df.dropna(how="all")

    # fill missing categories with empty strings
    df[CATEGORY_COLUMN] = (
        df[CATEGORY_COLUMN]
        .fillna("")
        .astype(str)
    )

    # split category column
    df[CATEGORY_COLUMN] = df[CATEGORY_COLUMN].str.split(";")

    expanded = df.explode(CATEGORY_COLUMN)

    # remove whitespace around categories
    expanded[CATEGORY_COLUMN] = (
        expanded[CATEGORY_COLUMN]
        .str.strip()
    )

    # remove blank categories
    expanded = expanded[
        expanded[CATEGORY_COLUMN] != ""
    ]

    # create ZIP file in memory
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w"
    ) as zip_file:

        # export full spreadsheet
        zip_file.writestr(
            "All_Expanded.csv",
            expanded.to_csv(index=False)
        )

        # export one file per category
        for category in sorted(
            expanded[CATEGORY_COLUMN].unique()
        ):

            subset = expanded[
                expanded[CATEGORY_COLUMN] == category
            ].copy()

            # remove duplicate emails
            if EMAIL_COLUMN in subset.columns:
                subset = subset.drop_duplicates(
                    subset=[EMAIL_COLUMN]
                )

            # clean filename
            safe_name = (
                category
                .replace("/", "-")
                .replace("\\", "-")
                .replace(":", "")
                .replace("*", "")
                .replace("?", "")
                .replace('"', "")
                .replace("<", "")
                .replace(">", "")
                .replace("|", "")
            )

            zip_file.writestr(
                f"{safe_name}.csv",
                subset.to_csv(index=False)
            )

    st.success(
        f"Created {len(expanded[CATEGORY_COLUMN].unique())} category files!"
    )

    st.download_button(
        label="Download CSV Files",
        data=zip_buffer.getvalue(),
        file_name="category_exports.zip",
        mime="application/zip"
    )
