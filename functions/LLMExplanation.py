# coding=utf-8
# Copyright 2018-2023 EvaDB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os

import pandas as pd
from retry import retry

from evadb.catalog.catalog_type import NdArrayType
# from evadb.configuration.configuration_manager import ConfigurationManager
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
# from evadb.utils.generic_utils import try_to_import_openai

_VALID_CHAT_COMPLETION_MODEL = [
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-32k",
    "gpt-4-32k-0314",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0301",
]


class LLMExplanation(AbstractFunction):
    @property
    def name(self) -> str:
        return "LLMExplanation"

    # @setup(cacheable=True, function_type="text-generation", batchable=True)
    @setup(cacheable=False)
    def setup(
        self,
        model="gpt-3.5-turbo",
    ) -> None:
        assert model in _VALID_CHAT_COMPLETION_MODEL, f"Unsupported ChatGPT {model}"
        self.model = model

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["query", "requirement"],
                column_types=[
                    NdArrayType.STR,
                    NdArrayType.STR,
                ],
                column_shapes=[(None,), (None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                # columns=["ids", "score"],
                # column_types=[NdArrayType.STR, NdArrayType.STR],
                # column_shapes=[(None,), (None,)],
                columns=["response"],
                column_types=[
                    NdArrayType.STR,
                ],
                column_shapes=[(1,)],
            )
        ],
    )
    def forward(self, text_df):
        # print(text_df)
        import llm

        model = llm.get_model(self.model)
        model.key = os.environ['OPENAI_KEY']

        if text_df.empty or text_df.iloc[0] is None:
            raise ValueError("Input DF must be provided.")
        
        values_list = []
        output_dataframe = pd.DataFrame()

        def try_llm_prompt(command, system, temperature):
            return str(model.prompt(command, system=system, temperature=temperature))
        
        for index, row in text_df.iterrows():
            # print("============ printing row : ============ ", "system : ", llm_system[i][0])
            # print(row)
            # print("================================")

            query = text_df[text_df.columns[0]][0]
            requirement = row['requirement']

            full_prompt = f"Here is the criteria for grading: {requirement},\n {query}"
            system = "You are a Teaching Assistant."
            response = try_llm_prompt(full_prompt, system=system, temperature=0.5)
            
            print("llm feedback-response for rubric no." + str(index+1) + " : ", response)
            
            values_list.append(response)

        # print("!here!")
        # output_dataframe = pd.DataFrame(values_list, columns=['ids', 'score'])
        output_dataframe = pd.DataFrame({"response": values_list})
        # print(output_dataframe)
        return output_dataframe
