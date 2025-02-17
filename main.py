import os
import sys
import json
import csv
import pandas as pd
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel
from PyQt6.QtCore import Qt
import xml.etree.ElementTree as ET
combined_results_rider = []

class FileDialogExample(QMainWindow):
    CONFIG_FILE = "config.json"

    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadSavedPath()

    def initUI(self):
        self.setWindowTitle("Open Multiple Files")
        self.setGeometry(100, 100, 500, 400)

        # Button to open files
        self.button = QPushButton("Open Files", self)
        self.button.clicked.connect(self.openFileDialog)
        self.button.setGeometry(50, 150, 100, 30)

        # Button to select save path
        self.path_button = QPushButton("Select Save Path", self)
        self.path_button.clicked.connect(self.selectSavePath)
        self.path_button.setGeometry(200, 150, 150, 30)

        # Label to show selected path
        self.path_label = QLabel("Save Path: Not Selected!", self)
        self.path_label.setGeometry(50, 200, 400, 30)
        self.path_label.setStyleSheet("color: red;")
        self.path_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.save_path = None

    def selectSavePath(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)

        if dialog.exec():
            self.save_path = dialog.selectedFiles()[0]
            self.path_label.setText(f"Save Path: {self.save_path}")
            self.path_label.setStyleSheet("color: black;")
            self.savePathToConfig()
        else:
            self.path_label.setText("Save Path: Not Selected!")
            self.path_label.setStyleSheet("color: red;")

    def openFileDialog(self):
        if not self.save_path:
            self.path_label.setText("Save Path: Not Selected!")
            self.path_label.setStyleSheet("color: red;")
            return

        file = QFileDialog(self)
        file.setWindowTitle("Open Files")
        file.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file.setViewMode(QFileDialog.ViewMode.Detail)

        if file.exec():
            selected_files = file.selectedFiles()
            current_date = datetime.now().strftime("%d%m")
            combined_results = []
            powerbike_keywords = [
                "Airoh", "Arai", "Bell", "Broger", "FOX", "Held", "HJC", "IMX", "Kryptonite", "Ozone", "POD",
                "Rebelhorn", "RG Racing", "RST", "S100", "SP Connect", "Sw Motech","Leatt"
            ]
            for file_path in selected_files:

                if "givi" in file_path.lower() and file_path.lower().endswith('.xml'):
                    self.process_givi_xml(file_path)

                if "pe_export_tab_ext_v4" in file_path.lower() and file_path.lower().endswith('.txt'):
                    self.process_swmotech_txt(file_path)

                if "olek" in file_path.lower() and file_path.lower().endswith('.xml'):
                    self.process_olek_xml(file_path)

                if "modeka" in file_path.lower() and file_path.lower().endswith('.csv'):
                    self.process_modeka_csv(file_path)

                if "b2bike" in file_path.lower() and file_path.lower().endswith('.xlsx'):
                    self.process_b2bike_xlsx(file_path)

                if "ridkp" in file_path.lower() and file_path.lower().endswith('.xml'):
                    self.process_kp_xml(file_path)

                if "shoei" in file_path.lower() and file_path.lower().endswith('.csv'):
                    self.process_shoei_csv(file_path)

                if "rider" in file_path.lower() and file_path.lower().endswith('.xml'):
                    self.process_rider_xml(file_path)

                if "wilmat" in file_path.lower() and file_path.lower().endswith('.csv'):
                    print("wil")
                    self.process_wilmat_csv(file_path)

                if any(keyword.lower() in file_path.lower() for keyword in powerbike_keywords):
                    matched_keyword = next(
                        (keyword for keyword in powerbike_keywords if keyword.lower() in file_path.lower()), None
                    )
                    if matched_keyword and file_path.lower().endswith('.csv'):
                        try:
                            cleaned_file_path = self.clean_csv(file_path)
                            data = pd.read_csv(cleaned_file_path, delimiter=',', quotechar='"', encoding='ISO-8859-1')
                            if "Dostepnosc" in data.columns and "Indeks" in data.columns:
                                # print(data)
                                if matched_keyword != "Rebelhorn" and matched_keyword != "Airoh":

                                    result = data[
                                        (data["Dostepnosc"] != "0.00") &
                                        (data["Dostepnosc"] != "") &
                                        (data["Dostepnosc"] != "VAT23") &
                                        (data["Dostepnosc"] != "0.0") &
                                        (data["Dostepnosc"] != "0,0") &
                                        (data["Dostepnosc"] != "0") &
                                        (data["Dostepnosc"] > 0)
                                        ][["Indeks", "Dostepnosc"]]
                                else:
                                    result = data[
                                        (data["Dostepnosc"] != "0.00") &
                                        (data["Dostepnosc"] != "") &
                                        (data["Dostepnosc"] != "VAT23") &
                                        (data["Dostepnosc"] != "0.0") &
                                        (data["Dostepnosc"] != "0,0") &
                                        (data["Dostepnosc"] != "0")
                                        ][["Indeks", "Dostepnosc"]]
                                    print(result)
                                print(matched_keyword)
                                print(len(result))
                                result["m4"] = 4
                                # result = result.astype(str)
                                combined_results.append(result)
                                # print(combined_results)

                            os.remove(cleaned_file_path)
                        except Exception as e:
                            print(f"Error reading {file_path}: {e}")

            if combined_results:
                final_data = pd.concat(combined_results, ignore_index=True)

                # final_data = final_data.astype(str)

                current_date = datetime.now().strftime("%d%m")
                output_filename = os.path.join(self.save_path, f"{current_date} powerbike kz.csv")
                final_data.to_csv(output_filename, index=False)
                print(f"Combined data saved to {output_filename}")

            else:
                print("No valid data found to combine.")

    def process_kp_xml(self, file_path):
        try:
            data = pd.read_xml(file_path)
            if "kod" in data.columns and "stan" in data.columns:
                result = data[data["stan"] > 0][["kod", "stan"]]
                result["m4"] = 4  # Add m4 column

                # Save file as "rider kp.csv"
                output_filename = os.path.join(self.save_path, f"{datetime.now().strftime('%d%m')} rider kp.csv")
                result.to_csv(output_filename, index=False)
                print(f"KP data saved to {output_filename}")

            else:
                print(f"Missing required columns in {file_path}")

        except Exception as e:
            print(f"Error processing KP XML file {file_path}: {e}")

    def process_givi_xml(self, file_path):
            tree = ET.parse(file_path)
            root = tree.getroot()
            givi_data = []

            for offer in root.findall(".//o"):
                kod = offer.find("kod").text if offer.find("kod") is not None else ""
                stock = offer.attrib.get("stock", "0")
                givi_data.append({"kod": kod, "stock": stock})

            return pd.DataFrame(givi_data)

    def process_olek_xml(self, file_path):
        try:
            data = pd.read_xml(file_path)
            if "kod" in data.columns and "quantity" in data.columns:
                result = data[data["quantity"] > 0][["kod", "quantity"]]
                result["m4"] = 4
                output_filename = os.path.join(self.save_path, f"{datetime.now().strftime('%d%m')} olek kz.csv")
                result.to_csv(output_filename, index=False)
        except Exception as e:
            print(f"Error reading Olek XML file: {e}")

    def process_givi_xml(self, file_path):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            givi_data = []

            for offer in root.findall(".//o"):
                kod = offer.find("kod").text if offer.find("kod") is not None else ""
                stock = offer.attrib.get("stock", "0")
                givi_data.append({"kod": kod, "stock": int(stock)})

            if givi_data:
                df = pd.DataFrame(givi_data)
                df = df[df["stock"] > 0]  # Remove rows with 0 stock
                output_filename = os.path.join(self.save_path, f"{datetime.now().strftime('%d%m')} givi_stock.csv")
                df.to_csv(output_filename, index=False)
                print(f"Givi data saved to {output_filename}")
            else:
                print("No valid Givi data found.")
        except Exception as e:
            print(f"Error processing Givi XML file {file_path}: {e}")

    def process_shoei_csv(self, file_path):
        try:
            df = pd.read_csv(file_path, delimiter=';', quotechar='"', encoding='ISO-8859-1', skiprows=9)
            df = df.rename(columns={
                df.columns[0]: "EAN Code",
                df.columns[3]: "Free stock"
            })
            df = df[["EAN Code", "Free stock"]]

            df["Free stock"] = pd.to_numeric(df["Free stock"], errors='coerce').fillna(0).astype(int)
            df = df[df["Free stock"] > 0]  # Remove rows with 0 stock

            output_filename = os.path.join(self.save_path, f"{datetime.now().strftime('%d%m')} shoei_stock.csv")
            df.to_csv(output_filename, index=False)
            print(f"Shoei data saved to {output_filename}")
        except Exception as e:
            print(f"Error processing Shoei CSV file {file_path}: {e}")

    def process_swmotech_txt(self, file_path):
        try:
            # Read the TXT file assuming it's tab-separated
            data = pd.read_csv(file_path, delimiter='\t', quotechar='"', encoding='ISO-8859-1')

            # Ensure required columns exist
            if "BrandName" in data.columns and "ItemNumber" in data.columns and "Availability" in data.columns:
                # Replace all occurrences of "9+" with "10" in the Availability column
                data["Availability"] = data["Availability"].replace("9+", "10")

                # Filter for "SW-MOTECH" and positive Availability
                result = data[(data["BrandName"] == "SW-MOTECH") & (data["Availability"] != "0")][
                    ["ItemNumber", "Availability"]]

                # Add m4 column
                result["m4"] = 4

                # Save to CSV
                output_filename = os.path.join(self.save_path, f"{datetime.now().strftime('%d%m')} swmotech kz.csv")
                result.to_csv(output_filename, index=False)
                print(f"Filtered Sw Motech data saved to {output_filename}")

            else:
                print(f"Missing required columns in {file_path}")

        except Exception as e:
            print(f"Error processing Sw Motech TXT file {file_path}: {e}")

    def process_modeka_csv(self, file_path):
        try:
            data = pd.read_csv(file_path, delimiter=';', quotechar='"', encoding='ISO-8859-1')
            if "st_Dostepny" in data.columns and "tw_Symbol" in data.columns:
                result = data[data["st_Dostepny"] > 0][["tw_Symbol", "st_Dostepny"]]
                result["m4"] = 4
                output_filename = os.path.join(self.save_path, f"{datetime.now().strftime('%d%m')} modeka kz.csv")
                result.to_csv(output_filename, index=False)
        except Exception as e:
            print(f"Error reading Modeka CSV file: {e}")

    def process_b2bike_xlsx(self, file_path):
        try:
            data = pd.read_excel(file_path)
            valid_groups = ["Sidi", "Kriega", "Lampa", "Cardo", "FreedConn", "Knox", "Midland"]
            filtered_data = data[data["Grupa"].isin(valid_groups)]

            if "Symbol" in filtered_data.columns and "Stan MAG" in filtered_data.columns:
                result = filtered_data[filtered_data["Stan MAG"] != "0"][["Symbol", "Stan MAG"]]
                result["m4"] = 4
                output_filename = os.path.join(self.save_path, f"{datetime.now().strftime('%d%m')} b2bike kz.csv")
                result.to_csv(output_filename, index=False)
        except Exception as e:
            print(f"Error reading B2Bike XLSX file: {e}")

    def process_wilmat_csv(self, file_path):
        try:

            data = pd.read_csv(file_path, delimiter=';', quotechar='"', encoding='ISO-8859-1' ,skiprows=1)

            print(data)
            if "Symbol" in data.columns and "Stan" in data.columns:

                data["Stan"] = data["Stan"].replace("jest", "1")

                # Check if "Nazwa" contains either "LS2" or "SHAD"
                data = data[data["Nazwa"].str.contains("LS2|SHAD", na=False)]


                result = data[(data["Stan"] != "brak") & (data["Stan"] != "0")][["Symbol", "Stan"]]
                print("kurwa")
                result["m4"] = 4
                output_filename = os.path.join(self.save_path, f"{datetime.now().strftime('%d%m')} wilmat kz.csv")
                result.to_csv(output_filename, index=False)
                print(result)
        except Exception as e:
            print(f"Error reading Wilmat CSV file: {e}")

    def clean_csv(self, file_path):
        cleaned_file_path = "cleaned_" + os.path.basename(file_path)
        with open(file_path, 'r', encoding='ISO-8859-1') as infile, open(cleaned_file_path, 'w', encoding='ISO-8859-1', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            for row in reader:
                if len(row) < 15:
                    row.extend([''] * (15 - len(row)))
                row = row[:15]
                writer.writerow(row)
        return cleaned_file_path

    def savePathToConfig(self):
        try:
            with open(self.CONFIG_FILE, 'w') as config_file:
                json.dump({"save_path": self.save_path}, config_file)
        except Exception as e:
            print(f"Error saving configuration: {e}")

    def loadSavedPath(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as config_file:
                    config = json.load(config_file)
                    self.save_path = config.get("save_path", None)
                    if self.save_path:
                        self.path_label.setText(f"Save Path: {self.save_path}")
                        self.path_label.setStyleSheet("color: black;")
            except Exception as e:
                print(f"Error loading configuration: {e}")


def main():
    app = QApplication(sys.argv)
    window = FileDialogExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()