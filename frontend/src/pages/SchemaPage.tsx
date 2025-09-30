// import { Splitter, SplitterPanel } from 'primereact/splitter';
// import { JSX, useState } from 'react';
// import { FileUpload } from 'primereact/fileupload';
// import { Divider } from 'primereact/divider';
// import { Button } from 'primereact/button';
// import OutputContent from '@/components/dashboard/blueprints/schema/OutputContent';
// import { InputContent } from '@/components/dashboard/blueprints/schema/InputContent';

// /**
//  * SchemaPage component
//  *
//  * This component renders a page with two panels: one for displaying and uploading input data,
//  * and another for displaying and editing the desired output data structure.
//  *
//  * @component
//  * @returns {JSX.Element} The rendered component
//  */
// export function SchemaPage(): JSX.Element {
//     // State to hold the input data
//     const [inputData, setInputData] = useState({
//         version: '1.0',
//         data: {
//             client_first_name: 'Aron',
//             client_last_name: 'Bozogany',
//             client_address: 'Bozostraat 420 Bozotown',
//             account_balance: '€2.8',
//             account_creation: 'March 25th 2019 at 16:32',
//             age: '25',
//             married: 'false',
//         },
//     });

//     // State to hold the output data structure
//     const [outputData, setOutputData] = useState({
//         client_details: {
//             first_name: { type: 'String', examples: ['Aron'] },
//             last_name: { type: 'String', examples: ['Bozogany'] },
//             street: { type: 'String', examples: ['Bozostraat'] },
//             number: { type: 'Number', examples: ['420'] },
//             city: { type: 'String', examples: ['Bozotown'] },
//         },
//         account_details: {
//             created_at: { type: 'Date', examples: ['25/03/2019 16:32'] },
//         },
//     });

//     /**
//      * Handle file upload event
//      *
//      * @param {Object} event - The file upload event
//      */
//     const handleFileUpload = () => {
//         setInputData(inputData);
//     };

//     /**
//      * Get the next available category index
//      *
//      * @param {Object} data - The data object to check for existing categories
//      * @returns {number} - The next available index for a new category
//      */
//     const getNextAvailableCategoryIndex = (data) => {
//         const existingNumbers = new Set();
//         Object.keys(data).forEach((key) => {
//             const match = key.match(/^new_category_(\d+)$/);
//             if (match) {
//                 existingNumbers.add(Number(match[1]));
//             }
//         });

//         let newIndex = 0;
//         while (existingNumbers.has(newIndex)) {
//             newIndex++;
//         }

//         return newIndex;
//     };

//     return (
//         <Splitter style={{ height: 'calc(100vh - 64px)' }}>
//             <SplitterPanel className="flex overflow-auto">
//                 <div className="p-4 w-full overflow-y-auto">
//                     <h2>Parsed input data structure</h2>
//                     <h4>
//                         The output below tries to generalize the input data in a way so it is
//                         applicable to every entry in the dataset.
//                     </h4>
//                     <Divider />
//                     <InputContent data={inputData} />
//                     <Divider />
//                     <FileUpload
//                         mode="basic"
//                         chooseLabel="Upload CSV"
//                         accept=".csv"
//                         maxFileSize={1000000}
//                         customUpload
//                         uploadHandler={handleFileUpload}
//                     />
//                 </div>
//             </SplitterPanel>
//             <SplitterPanel className="flex overflow-auto">
//                 <div className="p-4 w-full overflow-y-auto">
//                     <h2>Desired output data structure</h2>
//                     <h4>
//                         Create the target data structure by specifying fields with corresponding
//                         types and example values. Categories can be nested within other categories.
//                     </h4>
//                     <Divider />

//                     <OutputContent data={outputData} setOutputData={setOutputData} />

//                     <div className="flex mt-3">
//                         <Button
//                             label="Add Root Category"
//                             className="w-1/2 mr-2"
//                             onClick={() => {
//                                 setOutputData((prevData) => {
//                                     const newIndex = getNextAvailableCategoryIndex(prevData);
//                                     return {
//                                         ...prevData,
//                                         [`new_category_${newIndex}`]: {},
//                                     };
//                                 });
//                             }}
//                         />
//                         <Button
//                             label="Generate and Edit Mapping"
//                             className="w-1/2"
//                             onClick={() => {
//                                 console.log(outputData);
//                             }}
//                         />
//                     </div>
//                 </div>
//             </SplitterPanel>
//         </Splitter>
//     );
// }

// export default SchemaPage;
