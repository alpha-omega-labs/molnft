// SPDX-License-Identifier: MIT
//MOLNFT EDITOR VERSION. GENESISL1 HIERARCHICAL NFT SMART CONTRACT 
//STORE AND QUERY MOLECULAR DATA AND METADATA IN BLOCKCHAIN STATE
pragma solidity ^0.8.18;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

// For base64 encoding of metadata
import "@openzeppelin/contracts/utils/Base64.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title MolNFT
 * @dev MolNFT is an ERC721 contract with parent-child relationships and on-chain molecular data and metadata storage made for GenesisL1 blockchain.
 */
contract MolNFT is ERC721Enumerable, Ownable {
    using Strings for uint256;

    struct NFTData {
        string IDCODE;
        string HEADER;
        string ACCESSION_DATE;
        string COMPOUND;
        string SOURCE;
        string AUTHOR_LIST;
        string RESOLUTION;
        string EXPERIMENT_TYPE;
        string SEQUENCE;
        string imageBase64;
        string fileBase64;  
    }

    uint256 public nextNFTId = 1;
    uint256 public nextChildId = 100_000_000;

    bool public onlyDeployerCanMint; // Restriction toggle for minting

    mapping(uint256 => NFTData) private nftData; // Metadata for each NFT
    mapping(uint256 => uint256[]) private children; // parentId -> array of child IDs
    mapping(uint256 => uint256) private parent;     // childId -> parentId
    uint256[] private allTokens;                    // Array to store all token IDs for searching

    // ------------------------ EDITOR ROLE -------------------------------------

    mapping(address => bool) private _editors;

    event EditorAdded(address indexed account);
    event EditorRemoved(address indexed account);

    modifier onlyEditor() {
        require(_editors[msg.sender], "Not an editor.");
        _;
    }

    // Events
    event ParentNFTMinted(address indexed owner, uint256 indexed tokenId);
    event ChildNFTMinted(address indexed owner, uint256 indexed tokenId, uint256 indexed parentId);

    /**
     * @dev Environment wants an argument for Ownable, we do Ownable(msg.sender).
     *      The deployer is the initial editor.
     */
    constructor() ERC721("MolNFT", "MNFT") Ownable(msg.sender) {
        _editors[msg.sender] = true;
        emit EditorAdded(msg.sender);
    }

    /**
     * @dev Restricts who can mint if 'onlyDeployerCanMint' is set to true.
     */
    function setOnlyDeployerCanMint(bool status) external onlyOwner {
        onlyDeployerCanMint = status;
    }

    /**
     * @dev Mints a new NFT.
     *      - If parentId == 0, mint a parent NFT.
     *      - If parentId != 0, mint a child NFT linked to that parent.
     *      - The new NFT is assigned to 'to' as its initial owner.
     */
    function mintNFT(
        address to,
        string memory IDCODE,
        string memory HEADER,
        string memory ACCESSION_DATE,
        string memory COMPOUND,
        string memory SOURCE,
        string memory AUTHOR_LIST,
        string memory RESOLUTION,
        string memory EXPERIMENT_TYPE,
        string memory SEQUENCE,       
        string memory imageBase64,
        string memory fileBase64,
        uint256 parentId
    ) external {
        // Must be an editor:
        require(_editors[msg.sender], "Minting is restricted to editors.");

        // Optionally also restrict to contract owner if onlyDeployerCanMint == true:
        if (onlyDeployerCanMint) {
            require(msg.sender == owner(), "Minting is restricted to the deployer.");
        }

        uint256 tokenId;
        if (parentId == 0) {
            // Mint a parent token
            tokenId = nextNFTId++;
        } else {
            // Mint a child token
            require(parentId < 100_000_000, "Child tokens cannot be parents.");
            require(tokenExists(parentId), "Parent NFT does not exist.");
            // Preserve original text: "Only the parent owner can link a child."
            // => This still requires that the caller (msg.sender) be the parent owner.
            require(ownerOf(parentId) == msg.sender, "Only the parent owner can link a child.");
            tokenId = nextChildId++;
            parent[tokenId] = parentId;
            children[parentId].push(tokenId);
        }

        // Mint to the specified address 'to'
        _safeMint(to, tokenId);

        // Store metadata
        nftData[tokenId] = NFTData(
            IDCODE,
            HEADER,
            ACCESSION_DATE,
            COMPOUND,
            SOURCE,
            AUTHOR_LIST,
            RESOLUTION,
            EXPERIMENT_TYPE,
            SEQUENCE,         
            imageBase64,
            fileBase64
        );

        allTokens.push(tokenId);

        // Emit event, referencing 'to' since that's the actual owner
        if (parentId == 0) {
            emit ParentNFTMinted(to, tokenId);
        } else {
            emit ChildNFTMinted(to, tokenId, parentId);
        }
    }

    /**
     * @dev Returns true if 'tokenId' exists, false otherwise.
     *      We use try/catch around 'ownerOf(tokenId)' to detect existence.
     */
    function tokenExists(uint256 tokenId) public view returns (bool) {
        try this.ownerOf(tokenId) returns (address) {
            return true;
        } catch {
            return false;
        }
    }

    /**
     * @dev tokenURI override: returns JSON metadata with embedded base64 image.
     *
     * Format:
     * {
     *   "name": data.IDCODE,
     *   "description": data.COMPOUND,
     *   "image": "data:image/jpeg;base64,<imageBase64>"
     * }
     */
    function tokenURI(uint256 tokenId)
        public
        view
        override
        returns (string memory)
    {
        require(tokenExists(tokenId), "Token does not exist.");

        NFTData memory data = nftData[tokenId];

        string memory json = string(abi.encodePacked(
            '{',
                '"name": "', data.IDCODE, '",',
                '"description": "', data.COMPOUND, '",',
                '"image": "data:image/jpeg;base64,', data.imageBase64, '"',
            '}'
        ));

        // Base64-encode the JSON
        string memory encodedJson = Base64.encode(bytes(json));

        // Return the data URI
        return string(abi.encodePacked("data:application/json;base64,", encodedJson));
    }

    // ------------------------ GETTERS & UPDATE --------------------------------

    function getMetadata(uint256 tokenId)
        external
        view
        returns (
            string memory IDCODE,
            string memory HEADER,
            string memory ACCESSION_DATE,
            string memory COMPOUND,
            string memory SOURCE,
            string memory AUTHOR_LIST,
            string memory RESOLUTION,
            string memory EXPERIMENT_TYPE,
            string memory SEQUENCE,       
            string memory imageBase64,
            string memory fileBase64
        )
    {
        require(tokenExists(tokenId), "Token does not exist.");
        NFTData storage data = nftData[tokenId];

        return (
            data.IDCODE,
            data.HEADER,
            data.ACCESSION_DATE,
            data.COMPOUND,
            data.SOURCE,
            data.AUTHOR_LIST,
            data.RESOLUTION,
            data.EXPERIMENT_TYPE,
            data.SEQUENCE,
            data.imageBase64,
            data.fileBase64
        );
    }

    /**
     * @dev Only an editor can update metadata now. The check for ownership is removed.
     */
    function updateMetadata(
        uint256 tokenId,
        string memory IDCODE,
        string memory HEADER,
        string memory ACCESSION_DATE,
        string memory COMPOUND,
        string memory SOURCE,
        string memory AUTHOR_LIST,
        string memory RESOLUTION,
        string memory EXPERIMENT_TYPE,
        string memory SEQUENCE,       
        string memory imageBase64,
        string memory fileBase64
    ) external {
        require(_editors[msg.sender], "Only an editor can update.");
        require(tokenExists(tokenId), "Token does not exist.");

        NFTData storage data = nftData[tokenId];

        data.IDCODE = IDCODE;
        data.HEADER = HEADER;
        data.ACCESSION_DATE = ACCESSION_DATE;
        data.COMPOUND = COMPOUND;
        data.SOURCE = SOURCE;
        data.AUTHOR_LIST = AUTHOR_LIST;
        data.RESOLUTION = RESOLUTION;
        data.EXPERIMENT_TYPE = EXPERIMENT_TYPE;
        data.SEQUENCE = SEQUENCE;
        data.imageBase64 = imageBase64;
        data.fileBase64 = fileBase64;
    }

    // ------------------------ PARENT / CHILD LOGIC ----------------------------

    function getChildren(uint256 parentId) external view returns (uint256[] memory childIds) {
        require(tokenExists(parentId), "Parent token does not exist.");
        return children[parentId];
    }

    function getChildrenPaginated(
        uint256 parentId,
        uint256 offset,
        uint256 limit
    ) external view returns (uint256[] memory childIds, uint256 total) {
        require(tokenExists(parentId), "Parent token does not exist.");

        uint256[] storage allChildIds = children[parentId];
        uint256 allChildIdsLength = allChildIds.length;
        total = allChildIdsLength;

        if (offset >= allChildIdsLength) {
            return (new uint256[](0), total);
        }

        uint256 end = offset + limit;
        if (end > allChildIdsLength) {
            end = allChildIdsLength;
        }

        childIds = new uint256[](end - offset);
        for (uint256 i = offset; i < end; i++) {
            childIds[i - offset] = allChildIds[i];
        }
    }

    function getParent(uint256 tokenId) external view returns (uint256) {
        require(tokenExists(tokenId), "Token does not exist.");
        return parent[tokenId];
    }

    // ------------------------ CONCAT FILES ------------------------------------

    function getCombinedData(uint256 parentId) external view returns (string memory combinedFileBase64) {
        require(parentId < 100_000_000, "Only parent NFTs can have combined files.");
        require(tokenExists(parentId), "Parent token does not exist.");

        NFTData storage parentData = nftData[parentId];
        combinedFileBase64 = parentData.fileBase64;

        uint256[] storage childIds = children[parentId];
        for (uint256 i = 0; i < childIds.length; i++) {
            NFTData storage childData = nftData[childIds[i]];
            combinedFileBase64 = string(abi.encodePacked(combinedFileBase64, childData.fileBase64));
        }
    }

    function getEntireNFT(uint256 parentId)
        external
        view
        returns (
            string memory IDCODE,
            string memory HEADER,
            string memory ACCESSION_DATE,
            string memory COMPOUND,
            string memory SOURCE,
            string memory AUTHOR_LIST,
            string memory RESOLUTION,
            string memory EXPERIMENT_TYPE,
            string memory SEQUENCE,        
            string memory imageBase64,
            string memory combinedFileBase64
        )
    {
        require(parentId < 100_000_000, "Only parent NFTs can be queried.");
        require(tokenExists(parentId), "Parent NFT does not exist.");

        NFTData storage parentData = nftData[parentId];

        IDCODE = parentData.IDCODE;
        HEADER = parentData.HEADER;
        ACCESSION_DATE = parentData.ACCESSION_DATE;
        COMPOUND = parentData.COMPOUND;
        SOURCE = parentData.SOURCE;
        AUTHOR_LIST = parentData.AUTHOR_LIST;
        RESOLUTION = parentData.RESOLUTION;
        EXPERIMENT_TYPE = parentData.EXPERIMENT_TYPE;
        SEQUENCE = parentData.SEQUENCE;
        imageBase64 = parentData.imageBase64;

        combinedFileBase64 = parentData.fileBase64;
        uint256[] storage childIds = children[parentId];
        for (uint256 i = 0; i < childIds.length; i++) {
            NFTData storage childData = nftData[childIds[i]];
            combinedFileBase64 = string(abi.encodePacked(combinedFileBase64, childData.fileBase64));
        }
    }

    // ------------------------ SEARCH ------------------------------------------

    function searchByIDCODE(string memory searchTerm) external view returns (uint256[] memory tokenIds) {
        return _searchField("IDCODE", searchTerm);
    }

    function searchByHEADER(string memory searchTerm) external view returns (uint256[] memory tokenIds) {
        return _searchField("HEADER", searchTerm);
    }

    function searchByACCESSION_DATE(string memory searchTerm) external view returns (uint256[] memory tokenIds) {
        return _searchField("ACCESSION_DATE", searchTerm);
    }

    function searchByCOMPOUND(string memory searchTerm) external view returns (uint256[] memory tokenIds) {
        return _searchField("COMPOUND", searchTerm);
    }

    function searchBySOURCE(string memory searchTerm) external view returns (uint256[] memory tokenIds) {
        return _searchField("SOURCE", searchTerm);
    }

    function searchByAUTHOR_LIST(string memory searchTerm) external view returns (uint256[] memory tokenIds) {
        return _searchField("AUTHOR_LIST", searchTerm);
    }

    function searchByRESOLUTION(string memory searchTerm) external view returns (uint256[] memory tokenIds) {
        return _searchField("RESOLUTION", searchTerm);
    }

    function searchByEXPERIMENT_TYPE(string memory searchTerm) external view returns (uint256[] memory tokenIds) {
        return _searchField("EXPERIMENT_TYPE", searchTerm);
    }

    function searchBySEQUENCE(string memory searchTerm) external view returns (uint256[] memory tokenIds) {
        return _searchField("SEQUENCE", searchTerm);
    }

    // --------------------- PAGINATED SEARCH -----------------------------------

    function searchByIDCODEPaginated(string memory searchTerm, uint256 offset, uint256 limit)
        external
        view
        returns (uint256[] memory tokenIds, uint256 total)
    {
        return _searchFieldPaginated("IDCODE", searchTerm, offset, limit);
    }

    function searchByHEADERPaginated(string memory searchTerm, uint256 offset, uint256 limit)
        external
        view
        returns (uint256[] memory tokenIds, uint256 total)
    {
        return _searchFieldPaginated("HEADER", searchTerm, offset, limit);
    }

    function searchByACCESSION_DATEPaginated(string memory searchTerm, uint256 offset, uint256 limit)
        external
        view
        returns (uint256[] memory tokenIds, uint256 total)
    {
        return _searchFieldPaginated("ACCESSION_DATE", searchTerm, offset, limit);
    }

    function searchByCOMPOUNDPaginated(string memory searchTerm, uint256 offset, uint256 limit)
        external
        view
        returns (uint256[] memory tokenIds, uint256 total)
    {
        return _searchFieldPaginated("COMPOUND", searchTerm, offset, limit);
    }

    function searchBySOURCEPaginated(string memory searchTerm, uint256 offset, uint256 limit)
        external
        view
        returns (uint256[] memory tokenIds, uint256 total)
    {
        return _searchFieldPaginated("SOURCE", searchTerm, offset, limit);
    }

    function searchByAUTHOR_LISTPaginated(string memory searchTerm, uint256 offset, uint256 limit)
        external
        view
        returns (uint256[] memory tokenIds, uint256 total)
    {
        return _searchFieldPaginated("AUTHOR_LIST", searchTerm, offset, limit);
    }

    function searchByRESOLUTIONPaginated(string memory searchTerm, uint256 offset, uint256 limit)
        external
        view
        returns (uint256[] memory tokenIds, uint256 total)
    {
        return _searchFieldPaginated("RESOLUTION", searchTerm, offset, limit);
    }

    function searchByEXPERIMENT_TYPEPaginated(string memory searchTerm, uint256 offset, uint256 limit)
        external
        view
        returns (uint256[] memory tokenIds, uint256 total)
    {
        return _searchFieldPaginated("EXPERIMENT_TYPE", searchTerm, offset, limit);
    }

    function searchBySEQUENCEPaginated(string memory searchTerm, uint256 offset, uint256 limit)
        external
        view
        returns (uint256[] memory tokenIds, uint256 total)
    {
        return _searchFieldPaginated("SEQUENCE", searchTerm, offset, limit);
    }

    // --------------------- INTERNAL SEARCH HELPERS -----------------------------

    function _searchField(string memory field, string memory searchTerm)
        internal
        view
        returns (uint256[] memory)
    {
        string memory lowerSearchTerm = _toLower(searchTerm);
        uint256[] memory tempResults = new uint256[](allTokens.length);
        uint256 count = 0;

        for (uint256 i = 0; i < allTokens.length; i++) {
            uint256 tokenId = allTokens[i];
            string memory currentValue = _getFieldValue(field, tokenId);
            if (_contains(_toLower(currentValue), lowerSearchTerm)) {
                tempResults[count] = tokenId;
                count++;
            }
        }

        // Copy results into a properly sized array
        uint256[] memory results = new uint256[](count);
        for (uint256 j = 0; j < count; j++) {
            results[j] = tempResults[j];
        }

        return results;
    }

    function _searchFieldPaginated(
        string memory field,
        string memory searchTerm,
        uint256 offset,
        uint256 limit
    ) internal view returns (uint256[] memory tokenIds, uint256 total) {
        uint256[] memory allMatches = _searchField(field, searchTerm);
        total = allMatches.length;

        if (offset >= total) {
            return (new uint256[](0), total);
        }
        uint256 end = offset + limit;
        if (end > total) {
            end = total;
        }

        uint256[] memory results = new uint256[](end - offset);
        for (uint256 i = offset; i < end; i++) {
            results[i - offset] = allMatches[i];
        }
        return (results, total);
    }

    /**
     * @dev Retrieves the string value from nftData for a given field name.
     */
    function _getFieldValue(string memory field, uint256 tokenId) internal view returns (string memory) {
        NFTData storage data = nftData[tokenId];

        if (_compareStrings(field, "IDCODE")) return data.IDCODE;
        if (_compareStrings(field, "HEADER")) return data.HEADER;
        if (_compareStrings(field, "ACCESSION_DATE")) return data.ACCESSION_DATE;
        if (_compareStrings(field, "COMPOUND")) return data.COMPOUND;
        if (_compareStrings(field, "SOURCE")) return data.SOURCE;
        if (_compareStrings(field, "AUTHOR_LIST")) return data.AUTHOR_LIST;
        if (_compareStrings(field, "RESOLUTION")) return data.RESOLUTION;
        if (_compareStrings(field, "EXPERIMENT_TYPE")) return data.EXPERIMENT_TYPE;
        if (_compareStrings(field, "SEQUENCE")) return data.SEQUENCE;
        return "";
    }

    // --------------------- STRING UTILITIES -----------------------------------

    function _compareStrings(string memory a, string memory b)
        internal
        pure
        returns (bool)
    {
        return keccak256(abi.encodePacked(a)) == keccak256(abi.encodePacked(b));
    }

    function _toLower(string memory str) internal pure returns (string memory) {
        bytes memory bStr = bytes(str);
        bytes memory bLower = new bytes(bStr.length);

        for (uint256 i = 0; i < bStr.length; i++) {
            // If it's uppercase ASCII (A-Z), convert to lowercase
            if (bStr[i] >= 0x41 && bStr[i] <= 0x5A) {
                bLower[i] = bytes1(uint8(bStr[i]) + 32);
            } else {
                bLower[i] = bStr[i];
            }
        }
        return string(bLower);
    }

    function _contains(string memory str, string memory searchTerm) internal pure returns (bool) {
        bytes memory strBytes = bytes(str);
        bytes memory searchTermBytes = bytes(searchTerm);

        if (searchTermBytes.length > strBytes.length) {
            return false;
        }

        for (uint256 i = 0; i <= strBytes.length - searchTermBytes.length; i++) {
            bool matchFound = true;
            for (uint256 j = 0; j < searchTermBytes.length; j++) {
                if (strBytes[i + j] != searchTermBytes[j]) {
                    matchFound = false;
                    break;
                }
            }
            if (matchFound) {
                return true;
            }
        }
        return false;
    }

    // --------------------- EDITOR MANAGEMENT ----------------------------------

    /**
     * @dev Allows an existing editor to add another editor.
     */
    function addEditor(address account) external onlyEditor {
        require(!_editors[account], "Already an editor.");
        _editors[account] = true;
        emit EditorAdded(account);
    }

    /**
     * @dev Allows an existing editor to remove another editor.
     */
    function removeEditor(address account) external onlyEditor {
        require(_editors[account], "Not an editor.");
        _editors[account] = false;
        emit EditorRemoved(account);
    }
    
    // ------------------------ BATCH TRANSFER FUNCTION ------------------------
    /**
     * @dev Batch transfers multiple NFTs from a single address to another.
     * This function loops over an array of token IDs and calls safeTransferFrom for each one.
     * Requirements:
     * - Caller must be the owner of the tokens or approved operator.
     * - Each token transfer is subject to the standard ERC721 transfer checks.
     * If any individual transfer fails, the entire transaction reverts.
     *
     * @param from Address sending the tokens.
     * @param to Address receiving the tokens.
     * @param tokenIds Array of token IDs to transfer.
     */
    function batchTransferFrom(
        address from,
        address to,
        uint256[] calldata tokenIds
    ) external {
        for (uint256 i = 0; i < tokenIds.length; i++) {
            safeTransferFrom(from, to, tokenIds[i]);
        }
    }
}
