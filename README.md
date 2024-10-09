# Long Texts Processor

This project is along texts processor that helps send long texts to AI tools using your own prompts. At the present time it works via the Openai API only.

The purpose of this project is to aide the user by dividing the text into multiple chunks that the API can consume.

The program will print the ouput into a file including a header with some information about the generated text.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/leroidubuffet/long_texts_digester.git
   ```
2. Set up and activate a Python virtual environment
3. Install dependencies
4. Add your Openai key to ./config/config

## Usage

1. Run the script:
```
python long_text_digester.py
```
2. Follow the prompts to enter the paths for the input text file, the prompt file, and the output file.
3. The script processes the input text and writes the response to the specified output file.

## Configuration

The configuration file is located in `.config/config`. Make sure to set it with your Openai key up before running the application.

**Note:** The configuration file is ignored by Git for security reasons.

## Utils

The utils folder currently contains a function that retrieves the Openai available models.

## Contributing

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).