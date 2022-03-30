//SPDX-License-Identifier:MIT

pragma solidity ^0.7.0;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is Ownable, VRFConsumerBase {
    address payable[] public players;
    address payable public recentWinner;
    uint256 randomness;
    uint256 public entryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;
    AggregatorV3Interface internal inrUsdPriceFeed;

    event RequestedRandomness(bytes32 requestId);

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    uint256 public fee;
    bytes32 public keyHash;

    constructor(
        address _ethUsdPriceFeedAddress,
        address _inrUsdPriceFeedAddress,
        address _vrfCoordinator,
        address _linkToken,
        bytes32 _keyHash,
        uint256 _fee
    ) VRFConsumerBase(_vrfCoordinator, _linkToken) {
        entryFee = 0;
        ethUsdPriceFeed = AggregatorV3Interface(_ethUsdPriceFeedAddress);
        inrUsdPriceFeed = AggregatorV3Interface(_inrUsdPriceFeedAddress);
        keyHash = _keyHash;
        fee = _fee;
        lottery_state = LOTTERY_STATE.CLOSED;
    }

    function enter() public payable {
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "Lottery Is Not Yet Started !"
        );
        // Rupee 100 minimum
        require(msg.value >= entryFee, "Not Enough Money To Enter Lottery!");
        players.push(payable(msg.sender));
    }

    function inrToUsd() public view returns (uint256) {
        (, int256 usdPrice, , , ) = inrUsdPriceFeed.latestRoundData();
        return uint256(usdPrice);
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint256 inrToethPrice = ((inrToUsd() * 10**18) / uint256(price)); //in 18 decimals wei
        uint256 costToEnter = 100 * inrToethPrice;
        return uint256(costToEnter);
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Can't Start Lottery Yet!"
        );
        entryFee = getEntranceFee();
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyHash, fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "Can Not Complete Request"
        );
        require(_randomness > 0, "Random Not Found !");

        uint256 winnerIndex = _randomness % players.length;
        recentWinner = players[winnerIndex];

        recentWinner.transfer(address(this).balance);

        randomness = _randomness;
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
    }
}
