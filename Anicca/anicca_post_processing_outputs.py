import os
import pandas as pd
import matplotlib.pyplot as plt

class GraphPlotter:
    def __init__(self, base_dir):
        """
        Initializes the GraphPlotter with dynamic directory paths.

        This method sets up the initial directory paths based on the provided base directory.
        It initializes the base directory, and placeholders for the selected scenario directory,
        dataset directory, and graphs directory.

        Args:
            base_dir (str): The base directory path where scenario folders are located.
            selected_scenario_dir (str): The selected scenario directory path.
            dataset_dir (str): The dataset directory path.
            graphs_dir (str): The graphs directory path.
        """
        self.base_dir = base_dir
        self.selected_scenario_dir = ""
        self.dataset_dir = ""
        self.graphs_dir = ""

    def create_directory(self, directory_path):
        """
        Creates a directory if it does not exist.

        This method checks if a directory at the specified path exists, and if not, creates it.
        This ensures that the required directory structure is in place for saving graphs.

        Args:
            directory_path (str): The path of the directory to create.
        """
        os.makedirs(directory_path, exist_ok=True)

    def list_directories(self, directory_path):
        """
        Lists all directories in a specified directory.

        This method scans the given directory path and returns a list of all
        subdirectories. It filters out files and only includes directories.

        Args:
            directory_path (str): The path of the directory to search.

        Returns:
            list: A list of directory names found in the specified path.
        """
        return [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]

    def list_files(self, directory_path, extension='.xlsx'):
        """
        Lists all files in a directory with a specific extension.

        This method scans the given directory path and returns a list of all
        files that have the specified extension. It is used to find all relevant
        Excel files in the dataset directory.

        Args:
            directory_path (str): The path of the directory to search.
            extension (str, optional): The file extension to filter by. Defaults to '.xlsx'.

        Returns:
            list: A list of filenames with the specified extension.
        """
        return [f for f in os.listdir(directory_path) if f.endswith(extension)]

    def select_option(self, prompt, options):
        """
        Displays a list of options and prompts the user to select one.

        This method presents a prompt message and a list of options to the user.
        It waits for the user to input a selection and returns the index of the selected option.

        Args:
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
        Prompts the user to select a scenario folder and sets up directories.

        This method lists all scenario directories in the base directory and prompts
        the user to select one. Based on the user's selection, it sets up the paths
        for the dataset directory and graphs directory. It also creates the graphs
        directory if it does not exist.
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
        Plots a single graph based on user-selected file, sheet, and variable.

        This method:
        1. Lists all available Excel files in the dataset directory.
        2. Prompts the user to select one of these files.
        3. Loads the selected Excel file and lists all available sheets.
        4. Prompts the user to select one of these sheets.
        5. Loads the selected sheet into a DataFrame and lists all columns.
        6. Prompts the user to select one of these columns (variables).
        7. Extracts the selected column and the first column (assumed to be the x-axis) for plotting.
        8. Creates and displays a line plot for the selected variable against the x-axis.

        The graph includes labels, a legend, a title, and grid lines for better readability.
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
                    plt.xlim(2000, 2100)
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
        Plots multiple graphs for all files, sheets, and variables in the directory.

        This method:
        1. Lists all available Excel files in the dataset directory.
        2. Iterates through each file and loads it.
        3. Lists all sheets in the current file and iterates through each sheet.
        4. Loads the current sheet into a DataFrame and lists all columns.
        5. Iterates through each column (except the first one assumed to be the x-axis).
        6. Extracts the selected column and the first column (assumed to be the x-axis) for plotting.
        7. Creates a line plot for each variable against the x-axis and saves the plot as a PNG file.

        The saved graphs include labels, legends, titles, and grid lines for better readability.
        Each graph is saved in the graphs directory with a filename indicating the file, sheet, and variable.
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
                    plt.xlim(2000, 2100)
                    plt.grid(True)
                    graph_path = os.path.join(self.graphs_dir, f'{file}_{sheet}_{col}.png')
                    plt.savefig(graph_path)
                    plt.close()
        print(f"Graphs saved in {self.graphs_dir}")

def main():
    """
    Main function to execute the script. 

    This function:
    1. Initializes the base directory path.
    2. Creates an instance of GraphPlotter with the base directory.
    3. Prompts the user to select a scenario folder.
    4. Prompts the user to choose between single or multiple graph plotting.
    5. Executes the corresponding plotting method based on user choice.
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
