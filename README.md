# ESP-IDF Installation Procedure: 

> Source: [Link](https://github.com/espressif/vscode-esp-idf-extension/blob/master/docs/tutorial/install.md)

> **NOTE:** [troubleshooting](../../README.md#Troubleshooting)

1. Download and install [Visual Studio Code](https://code.visualstudio.com/).
2. Open the **Extensions** view by clicking on the Extension icon in the Activity Bar on the side of Visual Studio Code or the **View: Extensions** command <kbd>⇧</kbd> <kbd>⌘</kbd> <kbd>X</kbd>.
3. Search the extension with any related keyword like `espressif`, `esp-idf`, `esp32`, `esp32s2`, etc.
4. Install the extension.

5. Install [ESP-IDF Prerequisites](../../README.md#Prerequisites) and, if using WSL2, the required packages specified in [WSL Documentation](../WSL.md).


6. (OPTIONAL) Press <kbd>F1</kbd> and type **ESP-IDF: Select where to save configuration settings**, which can be User settings, Workspace settings or workspace folder settings. Please take a look at [Working with multiple projects](../MULTI_PROJECTS.md) for more information. Default is User settings.
7. In Visual Studio Code, select menu "View" and "Command Palette" and type [configure esp-idf extension]. After, choose the **ESP-IDF: Configure ESP-IDF extension** option. You can also choose where to save settings in the setup wizard.
8. Now the setup wizard window will be shown with several setup options: **Express**, **Advanced** or **Use existing setup**.

> **NOTE**: **Use existing setup** setup mode option is only shown if:
>
> - `esp-idf.json` is found in the current `idf.toolsPath` (MacOS/Linux users) or `idf.toolsPathWin` (Windows users). This file is generated when you install ESP-IDF with the [IDF Windows installer](https://github.com/espressif/idf-installer) or using [IDF-ENV](https://github.com/espressif/idf-env).
> - ESP-IDF is found in `idf.espIdfPath` or `idf.espIdfPathWin`, `IDF_PATH` environment variable, `$HOME/esp/esp-idf` on MacOS/Linux and `%USERPROFILE%\esp\esp-idf` or `%USERPROFILE%\Desktop\esp-idf` in Windows.
> - ESP-IDF Tools and ESP-IDF Python virtual environment for the previous ESP-IDF are found in `idf.toolsPath` or`idf.toolsPathWin`, `IDF_TOOLS_PATH` environment variable, `$HOME\.espressif` on MacOS/Linux and `%USERPROFILE%\.espressif` on Windows.



9. Choose **Express** for the fastest option (or **Use existing setup** if ESP-IDF is already installed)
10. If you choose **Express** setup mode:
    - Pick an ESP-IDF version to download (or find ESP-IDF in your system) and the python executable to create the virtual environment.
    - Choose the location for ESP-IDF Tools and python virtual environment (also known as `IDF_TOOLS_PATH`) which is `$HOME\.espressif` on MacOS/Linux and `%USERPROFILE%\.espressif` on Windows by default.
      > **NOTE:** Windows users don't need to select a python executable since it is part of the setup.

> **NOTE:** Make sure that `IDF_PATH` and `IDF_TOOLS_PATH` doesn't have any spaces to avoid any build issues.



11. The user will see a page showing the setup progress status showing ESP-IDF download progress, ESP-IDF Tools download and install progress as well as the creation of a python virtual environment.


12. (OPTIONAL) If the user have chosen the **Advanced** option, after ESP-IDF is downloaded and extracted, select to either download ESP-IDF Tools or manually provide each ESP-IDF tool absolute path and required environment variables.
    > **NOTE:** Consider that `IDF_PATH` requires each ESP-IDF tool to be of the version described in `IDF_PATH`/tools/tools.json.
    > If it is desired to use a different ESP-IDF tool version, check [JSON Manual Configuration](../SETUP.md#JSON-Manual-Configuration)


13. (OPTIONAL) If the user has chosen the **Advanced** mode and selected to manually provide each ESP-IDF tool absolute path, please enter the executable container directory for each binary as shown below:
    > **NOTE:** Check [JSON Manual Configuration](../SETUP.md#JSON-Manual-Configuration) for more information.


14. If everything is installed correctly, the user will see a message that all settings have been configured. You can start using the extension.


> **NOTE**: The advance mode allows the user to choose to use existing ESP-IDF tools by manually entering each ESP-IDF tool absolute path. Make sure each ESP-IDF tool path doesn't have any spaces.

15. Now that the extension setup is finally done, check the [basic use](./basic_use.md) to learn how to use the SDK Configuration editor, build, flash and monitor your Espressif device.

> **NOTE**: Visual Studio Code has many places where to set configuration settings. This extension uses the `idf.saveScope` configuration setting to determine where to save settings, Global (User Settings), Workspace and WorkspaceFolder. Please review [vscode settings precedence](https://code.visualstudio.com/docs/getstarted/settings#_settings-precedence).

> **NOTE:** the setup wizard will install ESP-IDF Python packages, this extension (`EXTENSION_PATH`/requirements.txt) and ESP-IDF debug adapter (`EXTENSION_PATH`/esp_debug_adapter/requirements.txt) python packages. Make sure that if using an existing python virtual environment that installing these packages doesn't affect your virtual environment. The `EXTENSION_PATH` is:

- Windows: `%USERPROFILE%\.vscode\extensions\espressif.esp-idf-extension-VERSION`
- Linux & MacOSX: `$HOME/.vscode/extensions/espressif.esp-idf-extension-VERSION`

# Post Installation:

In the bottom bar of your window you can view the following icons:

<p>
  <img src="../../blob/main/media/panel.png" alt="Setup wizard">
</p>

1. ESP-IDF Select Port to use: This allows the user to select the available serial port where their device is connected.
2. ESP-IDF Select Espressif device target: This allows the user to set the device target.
3. ESP-IDF Current Project: This selects the current folder.
4. ESP-IDF SDK Configuration Editor
5. ESP-IDF Full Clean: This cleans the project whereby the user can build the project from the start.
6. ESP-IDF Build: This will compile the program code and will help in checking for potential errors.
7. ESP-IDF Select flash method: This allows the user to select the flash method from JTAG, UART, and DFU.
8. ESP-IDF flash device: This will download the project in the chip.
9. ESP-IDF Monitor device: This gives the serial output of the chip.
10. ESP-IDF Build, Flash, and Monitor
11. ESP-IDF Open ESP-IDF Terminal: Clicking on this icon opens the terminal. If the terminal was already opened then it refreshes the terminal.
12. ESP-IDF Execute custom task

# Build and Flash

We will first open the terminal by clicking the open ESP-IDF terminal icon. This opens the terminal which is very similar to the PowerShell. It has all the variables of the environment already set up.

### To Flash csi_send
```
cd csi_send
idf.py flash -b 115200 -p /dev/cu.usbmodem142101 monitor

```
> Follow the same procedure to flash csi_recv

### Data Parsing

> csi_data_read_parse.py can be used to parse data simultaneously from 2 ESP boards and save it as a CSV.

There are certain parameters that have to be set before the script is run:

```
ESP_NUM = Total ESPs used for data acquisition
Visualize = Set to True to generate dynamic CSI plots
path = Data Directory
serial_port = ESP port name
file_name = CSV save name
```

> This is a timer based aquisition script whose value can be modified.

```
"""Timer for data acquisition"""
timer = QTimer()
timer.singleShot(4000, app.quit)  # 10 seconds = 10,000 ms
```

### Data Processing

> The Data_Processing folder houses all the scripts used for CSI Processing

1. multi_plot.py & helper.py : Built on top of the code written by Aditya Arun (WCSNG) for CSI processing

2. NIST_plot.py : Based on the MATLAB CSI plotting script used by NIST 

3. test_plot.ipynb : Notebook used to test and debug plotting code

4. multi_plot_v2.py : Improved CSI plotter with packet statistics 

> Plot created with multi_plot_v2.py:

<p>
  <img src="../../blob/main/media/CSI_Plot.png" alt="Setup wizard">
</p>


