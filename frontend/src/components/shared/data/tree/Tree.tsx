import { Divider } from 'primereact/divider';
import { JSX, ReactNode, useId } from 'react';
import { Tooltip } from 'primereact/tooltip';
import styles from './Tree.module.css';

export type TreeNode = {
    icon?: string;
    content?: React.ReactNode;
    children?: TreeNode[];
    tooltip?: ReactNode | string;
    uploadProgress?: number;
    inputDefinition?: boolean;
};

type TreeNodeProps = {
    node: TreeNode;
    isFirst?: boolean;
    isLast?: boolean;
    isRoot?: boolean;
    isOnly?: boolean;
    isGreen?: boolean;
};

/**
 * A React component that renders a tree node structure with optional children,
 * tooltips, and customizable styles for root, first, last, and only nodes.
 *
 * @param {TreeNodeProps} props - The properties for the TreeNodeComponent.
 *
 * @returns {JSX.Element} A JSX element representing the tree node and its children.
 */
export function TreeNodeComponent({
    node,
    isFirst,
    isLast,
    isRoot = true,
    isOnly,
}: TreeNodeProps): JSX.Element {
    const id = useId();
    const hasChildren = node.children && node.children.length > 0;
    const childCount = node.children?.length || 0;

    const horizontalClasses = [
        styles['horizontal-line'],
        isFirst ? styles['left'] : '',
        isLast ? styles['right'] : '',
    ];

    const renderedNode = (
        <div className="flex flex-column w-full align-items-center">
            {!isRoot ||
                (childCount > 1 &&
                    (node.children?.some((child) => child.inputDefinition) ? (
                        <Divider
                            layout="vertical"
                            className={`${styles['vertical-line']} ${styles['green-line']}`}
                        />
                    ) : (
                        <Divider layout="vertical" className={styles['vertical-line']} />
                    )))}
            {node.tooltip && (
                <Tooltip position="top" target={`#${id}`}>
                    {node.tooltip}
                </Tooltip>
            )}
            {node.uploadProgress && (
                <h5>
                    {node.uploadProgress !== undefined ? `${Math.round(node.uploadProgress)}%` : ''}
                </h5>
            )}
            <div
                id={id}
                className={`${styles['tree-node']} ${isRoot ? styles.root : ''} ${node.inputDefinition ? styles.input : ''}`}
            >
                <i className={node.icon} />
                {node.content}
            </div>
            {!isRoot && (
                <Divider
                    layout="vertical"
                    className={`${styles['vertical-line']} ${node.inputDefinition ? styles['green-line'] : ''}`}
                />
            )}
            {!isOnly && !isRoot && (
                <Divider
                    layout="horizontal"
                    className={`${horizontalClasses.join(' ')} ${node.inputDefinition ? styles['green-line'] : ''}`}
                />
            )}
        </div>
    );

    return (
        <div className="flex flex-column align-items-center">
            {hasChildren && (
                <div className="flex flex-column align-items-center w-full">
                    <div className="flex w-full">
                        {node.children!.map((child, idx) => (
                            <div key={idx} className="flex flex-column w-full">
                                <TreeNodeComponent
                                    node={child}
                                    isFirst={idx === 0}
                                    isOnly={childCount === 1}
                                    isLast={idx === childCount - 1}
                                    isRoot={false}
                                    isGreen={child.inputDefinition}
                                />
                            </div>
                        ))}
                    </div>

                    {!isRoot && (
                        <Divider
                            layout="vertical"
                            className={`${styles['vertical-line']} ${node.inputDefinition ? styles['green-line'] : ''}`}
                        />
                    )}
                </div>
            )}

            {renderedNode}
        </div>
    );
}
