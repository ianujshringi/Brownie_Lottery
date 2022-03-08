//SPDX-License-Identifier:MIT

pragma solidity ^0.7.0;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is Ownable {
    address payable[] public players;
    uint256 public entryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;
    AggregatorV3Interface internal inrUsdPriceFeed;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    constructor(
        address _ethUsdPriceFeedAddress,
        address _inrUsdPriceFeedAddress
    ) {
        entryFee = 0;
        ethUsdPriceFeed = AggregatorV3Interface(_ethUsdPriceFeedAddress);
        inrUsdPriceFeed = AggregatorV3Interface(_inrUsdPriceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
    }

    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN);
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
        return costToEnter;
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Can't Start Lottery Yet!"
        );
        entryFee = getEntranceFee();
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {}
}
