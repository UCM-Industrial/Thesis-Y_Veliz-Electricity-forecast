import os
import pandas as pd
import matplotlib.pyplot as plt

class GraphPlotter:
    def __init__(self, base_dir):
        """
        Initialize the GraphPlotter with dynamic directory paths.

        Parameters:
        base_dir (str): The base directory path where scenario folders are located.
        """
        self.base_dir = base_dir
        self.selected_scenario_dir = ""
        self.dataset_dir = ""
        self.graphs_dir = ""

    def create_directory(self, directory_path):
        """
        Create a directory if it does not exist.

        Parameters:
        directory_path (str): The path of the directory to create.
        """
        os.makedirs(directory_path, exist_ok=True)

    def list_directories(self, directory_path):
        """
        List all directories in a directory.

        Parameters:
        directory_path (str): The path of the directory to search.

        Returns:
        list: A list of directory names.
        """
        return [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]

    def list_files(self, directory_path, extension='.xlsx'):
        """
        List all files in a directory with a specific extension.

        Parameters:
        directory_path (str): The path of the directory to search.
        extension (str): The file extension to filter by.

        Returns:
        list: A list of filenames with the specified extension.
        """
        return [f for f in os.listdir(directory_path) if f.endswith(extension)]

    def select_option(self, prompt, options):
        """
        Display a list of options and prompt the user to select one.

        Parameters:
        prompt (str): The prompt message to display.
        options (list): A list of options to display.

        Returns:
        int: The index of the selected option.
        """
        print(prompt)
        for i, option in enumerate(options):
            print(f"{i + 1}. {option}")
        return int(input("Select an option: ")) - 1

    def select_scenario(self):
        """
        Prompt the user to select a scenario folder.
        """
        scenarios = self.list_directories(self.base_dir)
        selected_scenario_index = self.select_option("Select a scenario folder:", scenarios)

        if 0 <= selected_scenario_index < len(scenarios):
            self.selected_scenario_dir = os.path.join(self.base_dir, scenarios[selected_scenario_index])
            self.dataset_dir = os.path.join(self.selected_scenario_dir, "output")
            self.graphs_dir = os.path.join(self.selected_scenario_dir, "graphs")
            self.create_directory(self.graphs_dir)
        else:
            print("Invalid scenario")

    def plot_single_graph(self):
        """
        Plot a single graph based on user-selected file, sheet, and variable.
        """
        files = self.list_files(self.dataset_dir)
        selected_file_index = self.select_option("Available files are:", files)

        if 0 <= selected_file_index < len(files):
            selected_file = files[selected_file_index]
            file_path = os.path.join(self.dataset_dir, selected_file)

            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            selected_sheet_index = self.select_option("Available sheets are:", sheet_names)

            if 0 <= selected_sheet_index < len(sheet_names):
                selected_sheet = sheet_names[selected_sheet_index]
                df = pd.read_excel(file_path, sheet_name=selected_sheet)

                columns = df.columns.tolist()
                selected_index = self.select_option("Available variables are:", columns)

                if 0 <= selected_index < len(columns):
                    selected_column = columns[selected_index]

                    x_values = df.iloc[:, 0]
                    y_values = df[selected_column]

                    plt.figure(figsize=(10, 6))
                    plt.plot(x_values, y_values)
                    plt.legend([selected_column])
                    plt.title(selected_column)
                    plt.xlabel('Year')
                    plt.ylabel(selected_column)
                    plt.xlim(2000, 2400)
                    plt.grid(True)
                    plt.show()
                else:
                    print("Invalid variable")
            else:
                print("Invalid sheet")
        else:
            print("Invalid file")

    def plot_multiple_graphs(self):
        """
        Plot multiple graphs for all files, sheets, and variables in the directory.
        """
        files = self.list_files(self.dataset_dir)
        for file in files:
            file_path = os.path.join(self.dataset_dir, file)
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names

            for sheet in sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet)
                columns = df.columns.tolist()

                for col in columns[1:]:  
                    x_values = df.iloc[:, 0]
                    y_values = df[col]

                    plt.figure(figsize=(10, 6))
                    plt.plot(x_values, y_values)
                    plt.legend([col])
                    plt.title(f'{file} - {sheet} - {col}')
                    plt.xlabel('Year')
                    plt.ylabel(col)
                    plt.xlim(2000, 2400)
                    plt.grid(True)
                    graph_path = os.path.join(self.graphs_dir, f'{file}_{sheet}_{col}.png')
                    plt.savefig(graph_path)
                    plt.close()
        print(f"Graphs saved in {self.graphs_dir}")

def main():
    """
    Main function to execute the script. Prompts the user to choose a scenario,
    and then between single or multiple graph plotting, and executes the corresponding function.
    """
    base_dir = os.path.dirname(__file__)
    plotter = GraphPlotter(base_dir)

    plotter.select_scenario()

    print("Select the type of graph:")
    print("1. Single graph")
    print("2. Multiple graphs")

    plot_choice = int(input("Select an option (1 or 2): "))

    if plot_choice == 1:
        plotter.plot_single_graph()
    elif plot_choice == 2:
        plotter.plot_multiple_graphs()
    else:
        print("Invalid option")

if __name__ == "__main__":
    main()
