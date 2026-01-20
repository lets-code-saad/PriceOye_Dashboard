import streamlit as st


def colour_storage_filter(BASE_DF):
    filtered_df = BASE_DF.copy()

    # RAM / ROM FILTER
    ram_rom_list = st.session_state.get("selected_storage_combination", "")
    valid_pairs = []
    if ram_rom_list:
        for ram_rom_string in ram_rom_list:
            if not ram_rom_string:
                continue

            if ram_rom_string:
                ram_rom_parts = ram_rom_string.split("-")
                ram_string = (
                    ram_rom_parts[0].replace("GB", "").replace("RAM", "").strip()
                )
                ram = int(float(ram_string)) if ram_string else None
                # 6.0GB RAM - 128.0GB ROM

                rom_string = (
                    ram_rom_parts[1].replace("GB", "").replace("ROM", "").strip()
                )
                rom = int(float(rom_string)) if rom_string else None

                valid_pairs.append((ram, rom))

        filtered_df = filtered_df[
            filtered_df[["RAM", "ROM"]].apply(tuple, axis=1).isin(valid_pairs)
        ]

    return filtered_df
